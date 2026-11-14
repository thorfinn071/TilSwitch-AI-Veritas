from __future__ import annotations

import bz2
import csv
import io
import os
import tarfile
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from .types import InputError, RunConfig, file_sha, read_json, write_json

TATOEBA = "https://downloads.tatoeba.org/exports/per_language"
TATOEBA_LICENSE = "https://creativecommons.org/licenses/by/2.0/fr/"
SHARE_ALIKE = "https://creativecommons.org/licenses/by-sa/4.0/"
LANGUAGE_MAP = {"kaz": "kk", "rus": "ru", "eng": "en"}
FLORES_MAP = {"kaz_Cyrl": "kk", "rus_Cyrl": "ru", "eng_Latn": "en"}
KRCS_COMMIT = "9f4fea488bd85490c23ba33ebecc9362d901a21e"
KRCS_URL = f"https://raw.githubusercontent.com/madrugado/KRCS/{KRCS_COMMIT}"
MAX_SOURCE_BYTES = 80 * 1024 * 1024


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    license_url: str
    sha256: str | None = None


SENTENCES = [
    Source(f"{code}_sentences_detailed.tsv.bz2",
           f"{TATOEBA}/{code}/{code}_sentences_detailed.tsv.bz2", TATOEBA_LICENSE)
    for code in LANGUAGE_MAP
]
LINKS = [
    Source(f"{pair}_links.tsv.bz2", f"{TATOEBA}/{pair[:3]}/{pair}_links.tsv.bz2", TATOEBA_LICENSE)
    for pair in ("kaz-eng", "kaz-rus", "eng-rus")
]
FLORES = Source("flores200_dataset.tar.gz",
                "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz", SHARE_ALIKE,
                "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6")
KRCS = Source("KRCS.csv", f"{KRCS_URL}/KRCS.csv", f"{KRCS_URL}/LICENSE",
              "9f4eb200f0c52188bdd39aea33bf4d44a7da81f00eb5f00a98aa807da80ccc6d")


def _fetch(source: Source, directory: Path) -> dict:
    path = directory / source.name
    receipt_path = directory / f"{source.name}.json"
    if path.exists() and receipt_path.exists():
        receipt = read_json(receipt_path)
        if receipt["url"] != source.url or receipt["sha256"] != file_sha(path):
            raise InputError(f"Cached source differs from its receipt: {source.name}")
        if source.sha256 and receipt["sha256"] != source.sha256:
            raise InputError(f"Pinned source hash differs: {source.name}")
        return receipt

    request = Request(source.url, headers={"User-Agent": "TilSwitch AI research reproducibility"})
    for attempt in range(2):
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
                tmp = Path(stream.name)
                with urlopen(request, timeout=30) as response:
                    written = 0
                    while chunk := response.read(1024 * 1024):
                        written += len(chunk)
                        if written > MAX_SOURCE_BYTES:
                            raise InputError(f"Source exceeded the input limit: {source.name}")
                        stream.write(chunk)
                    modified = response.headers.get("Last-Modified")
                    advertised_length = response.headers.get("Content-Length")
                    if advertised_length and written != int(advertised_length):
                        raise OSError("Download stopped before the advertised length.")
            checksum = file_sha(tmp)
            if source.sha256 and source.sha256 != checksum:
                raise InputError(f"Download checksum did not match: {source.name}")
            receipt = {**asdict(source), "schema_version": 1, "sha256": checksum,
                       "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                       "last_modified": modified, "size_bytes": tmp.stat().st_size}
            os.replace(tmp, path)
            write_json(receipt_path, receipt)
            return receipt
        except OSError as error:
            if attempt == 1:
                raise OSError(f"Could not fetch {source.name}: {error}") from error
        finally:
            if tmp:
                tmp.unlink(missing_ok=True)
    raise AssertionError("unreachable")


def fetch_sources(cfg: RunConfig, review_only: bool = False, mono_only: bool = False) -> list[dict]:
    cfg.raw.mkdir(parents=True, exist_ok=True)
    selected = [] if mono_only else [KRCS]
    if not review_only:
        selected += [*SENTENCES, *LINKS] if cfg.source_set == "tatoeba" else [FLORES]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_fetch, source, cfg.raw) for source in selected]
        return [future.result() for future in futures]


def receipts(cfg: RunConfig) -> list[dict]:
    names = [KRCS, *SENTENCES, *LINKS] if cfg.source_set == "tatoeba" else [KRCS, FLORES]
    records = []
    for source in names:
        path = cfg.raw / source.name
        path_receipt = cfg.raw / f"{source.name}.json"
        if not path_receipt.is_file():
            if source is KRCS:
                continue
            raise InputError(f"Missing source receipt for {source.name}. Run fetch first.")
        record = read_json(path_receipt)
        if file_sha(path) != record["sha256"]:
            raise InputError(f"Raw source checksum mismatch: {source.name}")
        records.append(record)
    return records


def tatoeba_rows(path: Path, language_code: str, drops: Counter):
    with bz2.open(path, "rt", encoding="utf-8", newline="") as stream:
        for line in stream:
            values = line.rstrip("\r\n").split("\t")
            if len(values) != 6 or not values[0].isdigit() or values[1] != language_code:
                drops["bad_tatoeba_row"] += 1
                continue
            native_id, _, text, *_ = values
            yield {"message_id": f"tatoeba-{native_id}", "source_row_id": native_id, "text": text,
                   "source": "tatoeba", "source_lang": LANGUAGE_MAP[language_code],
                   "origin": "weak_public"}


def tatoeba_links(path: Path):
    with bz2.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            pair = line.rstrip("\n").split("\t")
            if len(pair) != 2 or not all(value.isdigit() for value in pair):
                raise InputError(f"Unexpected translation-link columns: {path.name}")
            yield f"tatoeba-{pair[0]}", f"tatoeba-{pair[1]}"


def flores_rows(path: Path):
    with tarfile.open(path, "r:gz") as archive:
        for split, size in (("dev", 997), ("devtest", 1012)):
            for code, language in FLORES_MAP.items():
                member = f"./flores200_dataset/{split}/{code}.{split}"
                stream = archive.extractfile(member)
                if stream is None:
                    raise InputError(f"Missing FLORES member: {member}")
                with io.TextIOWrapper(stream, encoding="utf-8") as reader:
                    lines = [line.rstrip("\r\n") for line in reader]
                if len(lines) != size:
                    raise InputError(f"Unexpected FLORES row count: {member}")
                for line_number, text in enumerate(lines, 1):
                    group = f"flores-{split}-{line_number}"
                    yield {"message_id": f"{group}-{language}", "source_row_id": str(line_number),
                           "text": text, "source": "flores", "source_lang": language,
                           "origin": "weak_public", "upstream_group": group, "upstream_split": split}


def krcs_rows(path: Path):
    if file_sha(path) != KRCS.sha256:
        raise InputError("KRCS source checksum differs from the verified author release.")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter=";")
        if next(reader, None) != ["", "Оригинал", "Перевод на казахский", "Перевод на русский"]:
            raise InputError("Unexpected KRCS columns.")
        for row in reader:
            if len(row) != 4 or not all(value.strip() for value in row):
                continue
            native_id, original, kazakh, russian = row
            yield {"message_id": f"krcs-{native_id}", "source_row_id": native_id,
                   "source": "krcs", "source_lang": None, "origin": "human_public",
                   "snapshot": KRCS_COMMIT, "text": original.strip(),
                   "translations": (kazakh.strip(), russian.strip())}
