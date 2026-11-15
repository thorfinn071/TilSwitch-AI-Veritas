"""Recheck the released review policy against the pinned KazNLP splits and local KRCS labels."""

import argparse
import csv
from collections import Counter
from dataclasses import replace
from pathlib import Path

from experiments.informal import authored_cases, evaluate
from tilswitch.evaluate import _review_inputs
from tilswitch.infer import analyze
from tilswitch.model import Policy, load_bundle
from tilswitch.prepare import duplicate_pairs, review_candidates, verified_split
from tilswitch.text import validate_text
from tilswitch.types import InputError, RunConfig, file_sha, read_json, read_rows


RECEIPT = Path("release/evidence/borrowing-review.json")


def read_external(folder, split, digest):
    path = folder / f"{split}.csv"
    if file_sha(path) != digest:
        raise InputError(f"The KazNLP {split} file differs from the pinned source.")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [row for row in csv.DictReader(stream)
                if row["source"] == "real" and row["language"] in {"kz", "ru", "mixed"}]


def screen(rows, known):
    start = len(known)
    inventory = known + [(row["label_id"], row["text"]) for row in rows]
    exclusions = {right - start for _, right in duplicate_pairs(inventory) if right >= start}
    valid = []
    invalid_count = 0
    for index, row in enumerate(rows):
        if index in exclusions:
            continue
        try:
            validate_text(row["text"])
        except InputError:
            invalid_count += 1
        else:
            valid.append(row)
    return valid, {"source_rows": len(rows), "duplicates": len(exclusions), "invalid": invalid_count}


def document_metrics(rows, model):
    groups = {"all": Counter(), "short": Counter()}
    borrowing_reviews = Counter()
    for row in rows:
        result = analyze(row["text"], model)
        cell = row["language"], result["primary_language"] or result["status"]
        groups["all"][cell] += 1
        if result["lexical_count"] <= 12:
            groups["short"][cell] += 1
        if any(token["reason"] == "kazakh_ending" for token in result["tokens"]):
            borrowing_reviews[row["language"]] += 1
    return {
        **{group: {label: {outcome: count for (reference, outcome), count in matrix.items() if reference == label}
                   for label in ("kz", "ru", "mixed")} for group, matrix in groups.items()},
        "messages_with_borrowing_review": dict(borrowing_reviews),
    }


def word_metrics(cases, model):
    summary = evaluate(cases, model)
    stats = summary["tokens"]
    return {**{key: stats[key] for key in ("macro_f1", "coverage", "accepted", "units")},
            "switch": summary["switch"], "switch_details": summary["switch_details"]}


def check(kaznlp_dir, baseline_bundle):
    receipt = read_json(RECEIPT)
    baseline = load_bundle(baseline_bundle, receipt["baseline_bundle"])
    candidate = replace(baseline, policy=Policy(**receipt["inference_policy"]))
    variants = {"release_v1": baseline, "selected_review_policy": candidate}
    cfg = RunConfig.load(Path("conf/experiment.json"))
    known = [(row["message_id"], row["text"]) for row in read_rows(verified_split(cfg, "train"))]
    known.extend((row["message_id"], row["text"]) for row in review_candidates(cfg, "krcs"))
    known.extend((row["message_id"], row["text"]) for split in ("dev", "test") for row in authored_cases(split))

    for name, author_split, local_split in (("development", "val", "dev"), ("test", "test", "test")):
        expected = receipt["results"][name]
        raw = read_external(kaznlp_dir, author_split, expected["kaznlp_sha256"])
        external, exclusions = screen(raw, known)
        known.extend((row["label_id"], row["text"]) for row in raw)
        reviewed = _review_inputs(cfg, "krcs", local_split)
        if reviewed is None or file_sha(reviewed[0]) != expected["krcs_sha256"]:
            raise InputError(f"The original, validated KRCS {local_split} labels are required.")
        current = {
            "external_filter": exclusions,
            "external": {key: document_metrics(external, candidate) for key, candidate in variants.items()},
            "krcs_local": {key: word_metrics(reviewed[2], candidate) for key, candidate in variants.items()},
            "authored": {key: word_metrics(authored_cases(local_split), candidate) for key, candidate in variants.items()},
        }
        if any(value != expected[key] for key, value in current.items()):
            raise InputError(f"Reproduced {name} counts differ from the evidence.")
        print(f"Matched {name}: {len(external)} KazNLP messages and the frozen KRCS and scripted comparisons.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kaznlp-dir", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=Path("artifacts/models/krcs-release"))
    args = parser.parse_args()
    try:
        check(args.kaznlp_dir, args.baseline)
    except (OSError, ValueError) as error:
        parser.exit(1, f"TilSwitch: {error}\n")
