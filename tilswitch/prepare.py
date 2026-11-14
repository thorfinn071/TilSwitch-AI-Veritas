from __future__ import annotations

import csv
import heapq
import math
from collections import Counter, defaultdict
from pathlib import Path

import regex

from . import sources
from .text import KAZAKH_LETTERS, normalize_word, tokenize
from .types import (
    GOLD_LABELS, LANGUAGES, SCHEMA, InputError, RunConfig, atomic_text, file_sha, new_artifact_dir,
    read_json, read_rows, stable_key, text_sha, write_json, write_rows,
)

PRIVATE = regex.compile(
    r"(?i)(?:https?://|www\.|@[\w]|(?:\+?\d[\s().-]*){8,}|[\w.+-]+@[\w.-]+\.\w{2,})"
)
SPREADSHEET_PREFIXES = ("=", "+", "-", "@")
CONTROL = regex.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\p{Bidi_Control}]")
LETTER = regex.compile(r"\p{L}")
WORD_SHAPE = regex.compile(r"\p{L}[\p{L}\p{M}'’\-]*")
REVIEW_FIELDS = (
    "message_id", "token_index", "start", "end", "surface", "text", "text_sha256",
    "label", "reason", "reviewer",
)
EXCEPTION_LABELS = {"ambiguous", "other", "unknown"}


def canonical(text: str) -> str:
    return " ".join(normalize_word(text).split())


def fingerprints(text: str) -> tuple[str, str]:
    exact = canonical(text)
    masked = regex.sub(r"\p{Nd}+", "<number>", PRIVATE.sub("<identifier>", exact))
    return exact, masked


def _grams(masked: str) -> frozenset[str]:
    if len(WORD_SHAPE.findall(masked)) < 5:
        return frozenset()
    return frozenset(masked[index:index + 4] for index in range(len(masked) - 3))


def duplicate_pairs(items: list[tuple[str, str]]):
    """Exact and masked matches plus a prefix-filtered 4-gram Jaccard join."""
    by_key = {}
    gram_sets = []
    frequencies = Counter()
    for index, (_, text) in enumerate(items):
        keys = fingerprints(text)
        for key in set(keys):
            prior = by_key.setdefault(key, index)
            if prior != index:
                yield prior, index
        grams = _grams(keys[1])
        gram_sets.append(grams)
        frequencies.update(grams)
    prefix_index = defaultdict(list)
    for index, grams in enumerate(gram_sets):
        if not grams:
            continue
        length = len(grams)
        prefix = sorted(grams, key=lambda gram: (frequencies[gram], gram))[:length - math.ceil(0.85 * length) + 1]
        candidates = {prior for gram in prefix for prior in prefix_index[gram]}
        for prior in sorted(candidates):
            older = gram_sets[prior]
            if min(length, len(older)) < 0.85 * max(length, len(older)):
                continue
            overlap = len(older & grams)
            if overlap >= 0.85 * (length + len(older) - overlap):
                yield prior, index
        for gram in prefix:
            prefix_index[gram].append(index)


class Groups:
    def __init__(self, keys):
        self.keys = list(keys)
        self.parents = list(range(len(self.keys)))

    def root(self, index):
        while self.parents[index] != index:
            self.parents[index] = self.parents[self.parents[index]]
            index = self.parents[index]
        return index

    def merge(self, left, right):
        left, right = self.root(left), self.root(right)
        if self.keys[left] > self.keys[right]:
            left, right = right, left
        self.parents[right] = left

    def name(self, index) -> str:
        return self.keys[self.root(index)]


def _sample_order(seed, row):
    return stable_key(seed, row["message_id"]), row["message_id"]


def _length(text: str) -> int:
    return sum(token.lexical for token in tokenize(text))


def _review_candidate(row):
    text = row["text"]
    if not 1 <= len(text) <= 300 or PRIVATE.search(text) or CONTROL.search(text):
        return False
    return 1 <= _length(text) <= 24


def _candidate_hash(rows):
    return text_sha("\n".join(f'{row["message_id"]}:{row["text_sha256"]}:{row["split"]}' for row in rows))


def _krcs_candidates(cfg: RunConfig) -> list[dict]:
    path = cfg.review / "krcs-candidates.jsonl"
    receipt_path = cfg.review / "krcs-candidates.json"
    if path.exists() and receipt_path.exists():
        return list(read_rows(path))
    if any((cfg.review / f"krcs-{split}.tsv").exists() for split in ("dev", "test")):
        raise InputError("Restore the frozen KRCS candidate inventory before editing or recreating review sheets.")
    seen = set()
    candidates = []
    for row in sources.krcs_rows(cfg.raw / sources.KRCS.name):
        if row["message_id"] in seen:
            raise InputError("Duplicate KRCS native ID.")
        seen.add(row["message_id"])
        if _review_candidate(row):
            candidates.append(row)
    candidates.sort(key=lambda row: _sample_order(cfg.split_seed, row))
    items = [(row["message_id"], row["text"]) for row in candidates]
    groups = Groups(key for key, _ in items)
    for left, right in duplicate_pairs(items):
        groups.merge(left, right)
    buckets = {"short": [], "long": []}
    used_groups = set()
    for index, row in enumerate(candidates):
        group = groups.name(index)
        if group in used_groups:
            continue
        used_groups.add(group)
        length = _length(row["text"])
        bucket = "short" if length <= 5 else "long"
        clean = {key: value for key, value in row.items() if key != "translations"}
        buckets[bucket].append({**clean, "group_id": group, "text_sha256": text_sha(row["text"]),
                                "lexical_count": length, "parent_ids": []})
    chosen = []
    for split, target in (("dev", cfg.external_dev_messages), ("test", cfg.external_test_messages)):
        short_target = target // 2
        short, long = buckets["short"], buckets["long"]
        short_count = min(len(short), max(short_target, target - len(long)))
        long_count = target - short_count
        if long_count > len(long):
            raise InputError(f"Not enough distinct screened KRCS rows to draw {split}.")
        rows = short[:short_count] + long[:long_count]
        del short[:short_count]
        del long[:long_count]
        chosen.extend({**row, "split": split} for row in sorted(rows, key=lambda r: _sample_order(cfg.split_seed, r)))
    write_rows(path, chosen)
    write_json(receipt_path, {
        "schema_version": SCHEMA, "candidate_file_sha256": file_sha(path),
        "inventory_id": _candidate_hash(chosen), "source_sha256": sources.KRCS.sha256,
        "seed": cfg.split_seed, "available_screened_rows": len(candidates),
        "policy_version": "v1", "counts": dict(Counter(row["split"] for row in chosen)),
    })
    return chosen


def _authored_candidates(cfg: RunConfig) -> list[dict]:
    path = cfg.review / "authored-candidates.jsonl"
    if not path.exists():
        raise InputError(f"Create {path} with message_id, family_id, split and text before export.")
    result = []
    families = {}
    ids = set()
    for row in read_rows(path):
        identifier = row.get("message_id")
        split = row.get("split")
        family = row.get("family_id")
        text = row.get("text")
        if (not isinstance(identifier, str) or not identifier or identifier in ids
                or split not in {"dev", "test"} or not isinstance(family, str) or not family
                or not isinstance(text, str) or not _review_candidate(row)):
            raise InputError("Invalid or duplicate authored review row.")
        if families.setdefault(family, split) != split:
            raise InputError("Authored scenario family crosses the dev/test boundary.")
        ids.add(identifier)
        result.append({"message_id": f"authored-{identifier}", "text": text, "split": split,
                       "text_sha256": text_sha(text), "group_id": f"authored-{family}",
                       "lexical_count": _length(text), "source": "team", "origin": "authored", "parent_ids": []})
    for i, j in duplicate_pairs([(row["message_id"], row["text"]) for row in result]):
        if result[i]["split"] != result[j]["split"]:
            raise InputError("Duplicate authored text crosses the dev/test boundary.")
    return result


def review_candidates(cfg: RunConfig, dataset: str) -> list[dict]:
    if dataset == "authored":
        return _authored_candidates(cfg)
    rows = _krcs_candidates(cfg)
    receipt = read_json(cfg.review / "krcs-candidates.json")
    if file_sha(cfg.review / "krcs-candidates.jsonl") != receipt["candidate_file_sha256"]:
        raise InputError("The frozen KRCS review inventory changed.")
    return rows


def _spreadsheet_literal(value: str) -> str:
    return "'" + value if value.lstrip().startswith(SPREADSHEET_PREFIXES) else value


def _review_rows(candidates, split):
    for row in candidates:
        if row["split"] != split:
            continue
        for index, token in enumerate(tokenize(row["text"])):
            yield {"message_id": row["message_id"], "token_index": str(index), "start": str(token.start),
                   "end": str(token.end), "surface": _spreadsheet_literal(token.text),
                   "text": _spreadsheet_literal(row["text"]),
                   "text_sha256": row["text_sha256"], "label": "" if token.lexical else "neutral",
                   "reason": "" if token.lexical else token.reason, "reviewer": ""}


def export_review(cfg: RunConfig, dataset: str, split: str) -> tuple[Path, int]:
    candidates = review_candidates(cfg, dataset)
    rows = list(_review_rows(candidates, split))
    if not rows:
        raise InputError(f"The {dataset} inventory has no {split} rows.")
    path = cfg.review / f"{dataset}-{split}.tsv"
    if not path.exists():
        with atomic_text(path) as stream:
            writer = csv.DictWriter(stream, REVIEW_FIELDS, dialect="excel-tab")
            writer.writeheader()
            writer.writerows(rows)
    return path, len({row["message_id"] for row in rows})


def gold_message_label(tokens):
    labels = {token["label"] for token in tokens}
    languages = labels.intersection(LANGUAGES)
    if len(languages) >= 2:
        return "mixed"
    if labels.intersection(EXCEPTION_LABELS):
        return "indeterminate"
    return "non_mixed" if languages else "neutral_only"


def validate_review(cfg: RunConfig, dataset: str, split: str) -> tuple[Path, dict]:
    candidates = review_candidates(cfg, dataset)
    expected = {(row["message_id"], row["token_index"]): row for row in _review_rows(candidates, split)}
    source_path = cfg.review / f"{dataset}-{split}.tsv"
    path = cfg.review / f"{dataset}-{split}.gold.jsonl"
    if not expected:
        raise InputError(f"No {split} rows in {dataset} inventory.")
    labels = defaultdict(list)
    reviewers = defaultdict(set)
    unfilled = []
    originals = {row["message_id"]: row["text"] for row in candidates if row["split"] == split}
    original_tokens = {message_id: tokenize(text) for message_id, text in originals.items()}
    with source_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, dialect="excel-tab")
        if reader.fieldnames != list(REVIEW_FIELDS):
            raise InputError("Review columns do not match the exported template.")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise InputError("A review row has misplaced or missing TSV columns.")
            key = row["message_id"], row["token_index"]
            expected_row = expected.pop(key, None)
            if expected_row is None:
                raise InputError(f"Review row or offsets changed: {key[0]} token {key[1]}.")
            token = original_tokens[key[0]][int(key[1])]
            if (any(row[field] != expected_row[field] for field in ("start", "end", "text_sha256"))
                    or row["surface"] not in (expected_row["surface"], token.text)
                    or row["text"] not in (expected_row["text"], originals[key[0]])):
                raise InputError(f"Review row or offsets changed: {key[0]} token {key[1]}.")
            label = row["label"].strip().lower()
            reason = row["reason"].strip()
            reviewer = row["reviewer"].strip()
            if not label or (not reviewer and expected_row["label"] != "neutral"):
                unfilled.append(key)
                continue
            if label not in GOLD_LABELS or (expected_row["label"] == "neutral" and label != "neutral"):
                raise InputError(f"Unexpected review label for {key[0]} token {key[1]}.")
            if label in EXCEPTION_LABELS and not reason:
                raise InputError(f"Add a reason for {key[0]} token {key[1]}.")
            if reviewer:
                reviewers[key[0]].add(reviewer)
            labels[key[0]].append({"token_index": int(key[1]), "start": int(row["start"]), "end": int(row["end"]),
                                    "text": token.text, "label": label, "reason": reason or None})
    if expected or unfilled:
        raise InputError(f"{dataset} {split} review is incomplete: {len(expected)} missing rows, "
                         f"{len(unfilled)} missing labels or reviewer codes.")
    output = []
    label_counts = Counter()
    label_messages = Counter()
    for row in candidates:
        if row["split"] != split:
            continue
        tokens = sorted(labels[row["message_id"]], key=lambda token: token["token_index"])
        label_counts.update(token["label"] for token in tokens)
        label_messages.update({token["label"] for token in tokens})
        output.append({**row, "tokens": tokens, "policy_version": "v1",
                       "reviewer_ids": sorted(reviewers[row["message_id"]]),
                       "message_label": gold_message_label(tokens)})
    write_rows(path, output)
    receipt = {"schema_version": SCHEMA, "dataset": dataset, "split": split,
               "policy_version": "v1", "gold_sha256": file_sha(path), "sheet_sha256": file_sha(source_path),
               "inventory_id": _candidate_hash(candidates), "messages": len(output),
               "short_messages": sum(row["lexical_count"] <= 5 for row in output),
               "label_counts": dict(label_counts), "label_messages": dict(label_messages)}
    write_json(path.with_suffix(".json"), receipt)
    return path, receipt


def _eligible_mono(row, drops):
    text, language = row["text"], row["source_lang"]
    if not 1 <= len(text) <= 300 or not LETTER.search(text) or PRIVATE.search(text) or CONTROL.search(text):
        drops["length_script_or_privacy"] += 1
        return False
    words = [token for token in tokenize(text) if token.lexical]
    expected = "latin" if language == "en" else "cyrillic"
    if not 1 <= len(words) <= 30 or any(token.script != expected for token in words):
        drops["lexical_count_or_wrong_script"] += 1
        return False
    if language == "ru" and KAZAKH_LETTERS.intersection(normalize_word(text)):
        drops["kazakh_letters_in_russian"] += 1
        return False
    return any(token.reason is None for token in words)


def _collect_mono(cfg, drops):
    if cfg.source_set == "flores":
        return [row for row in sources.flores_rows(cfg.raw / sources.FLORES.name) if _eligible_mono(row, drops)]
    found = []
    for code, source in zip(sources.LANGUAGE_MAP, sources.SENTENCES):
        candidate_count = min(cfg.candidate_limit, 4000) if code == "kaz" else cfg.candidate_limit
        rows = sources.tatoeba_rows(cfg.raw / source.name, code, drops)
        # Draw a larger deterministic sample cheaply before Unicode eligibility checks.
        sample = heapq.nsmallest(candidate_count * 4, rows, key=lambda row: _sample_order(cfg.split_seed, row))
        accepted = [row for row in sample if _eligible_mono(row, drops)]
        found.extend(accepted[:candidate_count])
    return found


def prepare(cfg: RunConfig) -> dict:
    source_receipts = sources.receipts(cfg)
    candidates = []
    if (cfg.raw / sources.KRCS.name).is_file():
        candidates.extend(review_candidates(cfg, "krcs"))
    if (cfg.review / "authored-candidates.jsonl").is_file():
        candidates.extend(review_candidates(cfg, "authored"))
    # Purge around the complete upstream KRCS file, including translations and unselected originals.
    protected = []
    if (cfg.raw / sources.KRCS.name).is_file():
        for row in sources.krcs_rows(cfg.raw / sources.KRCS.name):
            protected.extend((f'{row["message_id"]}-{index}', text)
                             for index, text in enumerate((row["text"], *row["translations"])))
    protected.extend((row["message_id"], row["text"]) for row in candidates if row["origin"] == "authored")
    drops = Counter()
    rows = _collect_mono(cfg, drops)
    row_ids = {row["message_id"]: index for index, row in enumerate(rows)}
    if len(row_ids) != len(rows):
        raise InputError("Duplicate monolingual source IDs.")
    items = [(row["message_id"], row["text"]) for row in rows] + protected
    groups = Groups(key for key, _ in items)
    for left, right in duplicate_pairs(items):
        groups.merge(left, right)
    parallel_links = 0
    if cfg.source_set == "tatoeba":
        for source in sources.LINKS:
            for left, right in sources.tatoeba_links(cfg.raw / source.name):
                if left in row_ids and right in row_ids:
                    groups.merge(row_ids[left], row_ids[right])
                    parallel_links += 1
    else:
        upstream = {}
        for index, row in enumerate(rows):
            original = upstream.setdefault(row["upstream_group"], index)
            if original != index:
                groups.merge(original, index)
                parallel_links += 1
    removed = {groups.root(index) for index in range(len(rows), len(items))}
    upstream_test = {groups.root(index) for index, row in enumerate(rows) if row.get("upstream_split") == "devtest"}
    exact_labels = defaultdict(set)
    for row in rows:
        exact_labels[canonical(row["text"])].add(row["source_lang"])
    selected = defaultdict(list)
    seen = set()
    for index, row in enumerate(rows):
        exact = canonical(row["text"])
        group_root = groups.root(index)
        if group_root in removed or len(exact_labels[exact]) > 1 or exact in seen:
            drops["protected_or_duplicate_or_conflicting"] += 1
            continue
        if cfg.source_set == "flores" and row["upstream_split"] == "dev" and group_root in upstream_test:
            drops["flores_overlap_with_devtest"] += 1
            continue
        seen.add(exact)
        group_id = groups.name(index)
        bucket = stable_key(cfg.split_seed, group_id) % 1000
        if cfg.source_set == "flores":
            split = "test" if row["upstream_split"] == "devtest" else "train" if bucket < 800 else "dev"
        else:
            split = "train" if bucket < 700 else "dev" if bucket < 850 else "test"
        selected[split, row["source_lang"]].append({**row, "split": split, "group_id": group_id,
                                                   "text_sha256": text_sha(row["text"]), "parent_ids": []})
    splits = {}
    counts = {}
    for split in ("train", "dev", "test"):
        limit = cfg.train_limit_per_language if split == "train" else cfg.dev_test_limit_per_language
        splits[split] = []
        counts[split] = {}
        for label in LANGUAGES:
            chosen = heapq.nsmallest(limit, selected[split, label], key=lambda row: _sample_order(cfg.split_seed, row))
            counts[split][label] = len(chosen)
            splits[split].extend(chosen)
        if not all(counts[split].values()):
            raise InputError(f"At least one class is empty in {split}. Inspect sources or choose FLORES.")
    group_roles = {}
    for split, split_rows in splits.items():
        for row in split_rows:
            if group_roles.setdefault(row["group_id"], split) != split:
                raise InputError("A grouped record crossed the split boundary.")
    with new_artifact_dir(cfg.prepared) as output:
        hashes = {}
        source_snapshots = {receipt["name"]: receipt["sha256"] for receipt in source_receipts}
        snapshot_id = text_sha("\n".join(f"{k}:{v}" for k, v in sorted(source_snapshots.items())))
        for split, split_rows in splits.items():
            path = output / f"{split}.jsonl"
            write_rows(path, ({**row, "snapshot": snapshot_id} for row in split_rows))
            hashes[split] = file_sha(path)
        manifest = {"schema_version": SCHEMA, "source_set": cfg.source_set, "seed": cfg.split_seed,
                    "source_receipts": source_receipts, "source_snapshot_id": snapshot_id,
                    "split_sha256": hashes, "counts": counts, "drops": dict(drops),
                    "parallel_links_in_pool": parallel_links,
                    "protected_texts": len(protected),
                    "review_inventory": {
                        name: _candidate_hash([row for row in candidates if row["source"] == name])
                        for name in sorted({row["source"] for row in candidates})
                    }}
        write_json(output / "manifest.json", manifest)
    return manifest


def verified_split(cfg: RunConfig, split: str):
    manifest = read_json(cfg.prepared / "manifest.json")
    path = cfg.prepared / f"{split}.jsonl"
    if file_sha(path) != manifest["split_sha256"][split]:
        raise InputError(f"Prepared {split} differs from its manifest.")
    return path
