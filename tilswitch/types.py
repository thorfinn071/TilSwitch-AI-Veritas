from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

LANGUAGES = ("kk", "ru", "en")
GOLD_LABELS = (*LANGUAGES, "neutral", "ambiguous", "other", "unknown")
SCHEMA = 1


class InputError(ValueError):
    """Invalid user text, configuration, dataset or artifact metadata."""


@dataclass(frozen=True)
class Token:
    start: int
    end: int
    text: str
    kind: str
    script: str | None = None
    reason: str | None = None

    @property
    def lexical(self) -> bool:
        return self.kind == "word"


def file_sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_key(seed: int, value: str) -> int:
    return int(text_sha(f"{seed}:{value}")[:16], 16)


def json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


@contextmanager
def atomic_text(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
    )
    temp = Path(stream.name)
    try:
        with stream:
            yield stream
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def new_artifact_dir(path: Path):
    """Publish a new complete artifact without modifying a prior result."""
    if path.exists():
        raise InputError(f"Output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent) as temporary:
        staging = Path(temporary) / path.name
        staging.mkdir()
        yield staging
        staging.rename(path)


def write_json(path: Path, value) -> None:
    with atomic_text(path) as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
        stream.write("\n")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except ValueError as error:
                raise InputError(f"Invalid JSON on line {line_number} in {path}") from error
            if not isinstance(row, dict):
                raise InputError(f"Expected a JSON object on line {line_number} in {path}")
            yield row


def write_rows(path: Path, rows) -> None:
    with atomic_text(path) as stream:
        for row in rows:
            stream.write(json_dump(row) + "\n")


@dataclass(frozen=True)
class RunConfig:
    schema_version: int
    source_set: str
    data_dir: Path
    artifact_dir: Path
    split_seed: int
    thresholds: tuple[float, ...]
    candidate_limit: int
    train_limit_per_language: int
    dev_test_limit_per_language: int
    train_tokens_per_language: int
    external_dev_messages: int
    external_test_messages: int
    max_features: int
    neighbor_weight: float

    @classmethod
    def load(cls, path: Path, source_set: str | None = None) -> RunConfig:
        raw = read_json(path)
        if not isinstance(raw, dict) or set(raw) != set(cls.__dataclass_fields__):
            raise InputError("Unexpected experiment configuration keys.")
        raw["source_set"] = source_set or raw["source_set"]
        if raw["schema_version"] != SCHEMA or raw["source_set"] not in ("tatoeba", "flores"):
            raise InputError("Unsupported config schema or source set.")
        for key in ("data_dir", "artifact_dir"):
            raw[key] = Path(raw[key])
        for key in set(raw) - {"schema_version", "source_set", "data_dir", "artifact_dir",
                               "thresholds", "neighbor_weight", "split_seed"}:
            if type(raw[key]) is not int or raw[key] < 1:
                raise InputError(f"{key} must be a positive integer.")
        thresholds = raw["thresholds"]
        if (not isinstance(thresholds, list) or not thresholds or thresholds[0] != 0
                or any(type(x) not in (int, float) or not 0 <= x <= 1 for x in thresholds)):
            raise InputError("Thresholds must start at zero and belong to [0, 1].")
        if not 0 <= raw["neighbor_weight"] <= 1 or raw["max_features"] > 30000:
            raise InputError("neighbor_weight must be in [0, 1] and max_features at most 30,000.")
        raw["thresholds"] = tuple(sorted(set(thresholds)))
        return cls(**raw)

    @property
    def raw(self) -> Path:
        return self.data_dir / "raw"

    @property
    def prepared(self) -> Path:
        return self.data_dir / "prepared" / self.source_set

    @property
    def review(self) -> Path:
        return self.data_dir / "review"

    @property
    def models(self) -> Path:
        return self.artifact_dir / "models"

    @property
    def runs(self) -> Path:
        return self.artifact_dir / "runs"
