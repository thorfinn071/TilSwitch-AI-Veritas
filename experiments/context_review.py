"""Compare fixed alert and context variants on development data."""

import argparse
from collections import Counter
from dataclasses import replace
from pathlib import Path

from experiments.informal import authored_cases
from tilswitch.evaluate import _aligned, summarize
from tilswitch.features import training_words
from tilswitch.infer import analyze
from tilswitch.model import load_bundle
from tilswitch.text import context_indices, group_segments, normalize_word, tokenize
from tilswitch.types import LANGUAGES, InputError, RunConfig, file_sha, read_rows, write_json

REVIEW = Path("artifacts/outputs/01a1de05-b3da-7d41-b14b-8a59a6292cf2/TilSwitch-reviewed-annotations.jsonl")
TRAIN = Path("data/prepared/tatoeba/train.jsonl")
KRCS_DEV = Path("data/review/krcs-dev.gold.jsonl")
DEV_HASHES = {
    TRAIN: "abf81e3da4780c949eef01d13edd26c2f5d270247645da2960ba79a05280e662",
    KRCS_DEV: "398fa041083bcc1d69eb789e33e23df73754c060ba3c87dc4e9a07b5c8d73ec9",
    REVIEW: "b8999bf8aba122f155a33400f3d8c6cef6c62eb08949540f4245ec21851dbc20",
}
REFERENCE_BUNDLE = Path("release/model")
SUBMISSION_BUNDLE = Path("release/submission/model")


def shared_conflict(text, result, shared):
    """Find a shared singleton next to two words in the other language."""
    counts = result["counts"]
    if result["status"] != "mixed" or counts["en"]:
        return None
    host, minority = sorted(("kk", "ru"), key=lambda label: -counts[label])
    if counts[host] < 2 or counts[minority] != 1:
        return None
    tokens = result["tokens"]
    index = next(i for i, token in enumerate(tokens) if token["label"] == minority)
    if normalize_word(tokens[index]["text"]) not in shared:
        return None
    neighbors = context_indices(text, tokenize(text))
    left, right = neighbors[index]
    if left is not None and right is not None:
        adjacent = (left, right)
    elif left is not None:
        adjacent = (neighbors[left][0], left)
    elif right is not None:
        adjacent = (right, neighbors[right][1])
    else:
        return None
    if all(i is not None and tokens[i]["label"] == host for i in adjacent):
        return index, host
    return None


def outcome(result):
    return result["primary_language"] or result["status"]


def spans(segments):
    return {(s["start"], s["end"], s["label"]) for s in segments if s["label"] in LANGUAGES}


def evaluate(cases, models, shared):
    rows = {name: [] for name in (*models, "shared_review", "shared_context_relabel")}
    phrase_totals = {name: Counter() for name in rows}
    for case in cases:
        text = case["text"]
        outputs = {name: analyze(text, model) for name, model in models.items()}
        gold = [
            {**token, "label": token["label"] if token["label"] in (*LANGUAGES, "neutral") else "unk"}
            for token in case["tokens"]
        ]
        reference_spans = spans(group_segments(text, gold))
        base = outputs["cutoff_035"]
        predictions = {
            name: (result["tokens"], result["segments"], outcome(result)) for name, result in outputs.items()
        }
        predictions["shared_review"] = predictions["cutoff_035"]
        predictions["shared_context_relabel"] = predictions["cutoff_035"]
        conflict = shared_conflict(text, base, shared)
        if conflict is not None:
            index, host = conflict
            predictions["shared_review"] = (base["tokens"], base["segments"], "possible_switch")
            if outputs["context"]["tokens"][index]["label"] == host:
                adjusted = base["tokens"].copy()
                adjusted[index] = {**adjusted[index], "label": host}
                status = "needs_review" if base["has_unknown"] else host
                predictions["shared_context_relabel"] = (adjusted, group_segments(text, adjusted), status)
        for name, (tokens, segments, predicted_outcome) in predictions.items():
            rows[name].append({
                "message_id": case["message_id"],
                "gold_message": case["message_label"],
                "outcome": predicted_outcome,
                "short": base["lexical_count"] <= 5,
                "tokens": _aligned(case, {"tokens": tokens}),
            })
            guesses = spans(segments)
            phrase_totals[name].update(correct=len(reference_spans & guesses), reference=len(reference_spans),
                                       predicted=len(guesses))

    report = {}
    for name, entries in rows.items():
        result = summarize(entries, reviewed=True)
        false_firm = Counter()
        one_word = Counter(all=0, firm=0)
        possible = 0
        lost_firm = 0
        for entry, base in zip(entries, rows["cutoff_035"], strict=True):
            possible += entry["outcome"] == "possible_switch"
            if entry["gold_message"] == "non_mixed":
                label = next(t["gold"] for t in entry["tokens"] if t["gold"] in LANGUAGES)
                false_firm[f"{label}_total"] += 1
                false_firm[f"{label}_firm"] += entry["outcome"] == "mixed"
            if entry["gold_message"] == "mixed" and base["outcome"] == "mixed":
                lost_firm += entry["outcome"] != "mixed"
            gold = Counter(token["gold"] for token in entry["tokens"])
            if (entry["gold_message"] == "mixed" and min(gold["kk"], gold["ru"]) == 1
                    and not any(gold[label] for label in ("en", "ambiguous", "other", "unknown"))):
                one_word["all"] += 1
                one_word["firm"] += entry["outcome"] == "mixed"
        report[name] = {
            "false_firm": dict(false_firm),
            "switch": result["switch"],
            "one_word": dict(one_word),
            "possible_switch": possible,
            "lost_baseline_firm_mixed": lost_firm,
            "tokens": result["tokens"],
            "exact_phrases": dict(phrase_totals[name]),
        }
    return report


def run(original, output):
    if output.exists():
        raise InputError(f"Choose a new development report path: {output}")
    digests = {str(path.as_posix()): file_sha(original / path) for path in DEV_HASHES}
    if any(digests[path.as_posix()] != digest for path, digest in DEV_HASHES.items()):
        raise InputError("A development or training input differs from the documented snapshot.")
    config = RunConfig.load(original / "conf/experiment.json")
    words = Counter((row.surface, label) for label, row in training_words(read_rows(original / TRAIN), config))
    shared = {word for (word, label), count in words.items()
              if label == "kk" and count >= 2 and words[word, "ru"] >= 2}
    release = load_bundle(SUBMISSION_BUNDLE)
    reference = load_bundle(REFERENCE_BUNDLE)
    context_path = original / "artifacts/models/context"
    context = load_bundle(context_path)
    if (release.policy.singleton_switch_margin != 0.35 or
            reference.policy.singleton_switch_margin != 0.20 or context.mode != "context"):
        raise InputError("Expected the saved 0.20, 0.35 and context artifacts.")
    context = replace(context, policy=replace(release.policy, review_kazakh_borrowings=False))
    models = {"script": None, "cutoff_020": reference, "cutoff_035": release, "context": context}
    cohorts = {
        "reviewed_development": [row for row in read_rows(original / REVIEW) if row["split"] == "development"],
        "krcs_development": list(read_rows(original / KRCS_DEV)),
        "authored_development": authored_cases("dev"),
    }
    if tuple(len(cases) for cases in cohorts.values()) != (60, 12, 12):
        raise InputError("Expected the same 60, 12 and 12 development examples.")
    write_json(output, {
        "phase": "development",
        "inputs_sha256": digests,
        "authored_fixture_sha256": file_sha(Path(__file__).with_name("informal-cases.jsonl")),
        "bundle_manifests_sha256": {
            "cutoff_020": file_sha(REFERENCE_BUNDLE / "manifest.json"),
            "cutoff_035": file_sha(SUBMISSION_BUNDLE / "manifest.json"),
            "context": file_sha(context_path / "manifest.json"),
        },
        "shared_training_spellings": len(shared),
        "cohorts": {name: {"messages": len(cases), "variants": evaluate(cases, models, shared)}
                    for name, cases in cohorts.items()},
    })
    print(f"Scored 84 development messages. Results: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        run(args.original, args.out)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"TilSwitch: {error}\n")
