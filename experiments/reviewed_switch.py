"""Compare two fixed Mixed alert cutoffs on the bilingual-reviewed holdout."""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from tilswitch.evaluate import predictions, summarize
from tilswitch.model import Policy, environment_receipt, load_bundle
from tilswitch.types import LANGUAGES, InputError, file_sha, new_artifact_dir, read_json, read_rows, write_json


ANNOTATIONS = (
    Path("artifacts/outputs/01a1de05-b3da-7d41-b14b-8a59a6292cf2") / "TilSwitch-reviewed-annotations.jsonl"
)
ANNOTATION_SHA = "b8999bf8aba122f155a33400f3d8c6cef6c62eb08949540f4245ec21851dbc20"
BUNDLE = Path("release/model")
BUNDLE_SHA = "ef4a9c31a9a7ecf724783b5c376d3e2af42b2150fe382b0dcf3f82bc8431c4bf"


def comparison_inputs():
    if file_sha(ANNOTATIONS) != ANNOTATION_SHA:
        raise InputError("The approved annotations differ from the reviewed snapshot.")
    model = load_bundle(BUNDLE, expected_sha=BUNDLE_SHA)
    if model.policy.singleton_switch_margin != 0.20:
        raise InputError("Expected the current 0.20 Mixed alert cutoff.")
    return model, {
        "annotations": ANNOTATIONS.as_posix(),
        "annotations_sha256": ANNOTATION_SHA,
        "split": "held_out",
        "expected_messages": 60,
        "bundle": BUNDLE.as_posix(),
        "bundle_manifest_sha256": BUNDLE_SHA,
        "model_id": model.model_id,
        "environment": environment_receipt(),
        "code_sha256": {
            path.as_posix(): file_sha(path)
            for path in [Path("experiments/reviewed_switch.py"), *sorted(Path("tilswitch").glob("*.py"))]
        },
        "policies": {
            "baseline": asdict(model.policy),
            "candidate": asdict(replace(model.policy, singleton_switch_margin=0.35)),
        },
        "decision_rule": "Fewer false Mixed alerts with at least as many genuine mixed and one-word switches flagged",
    }


def case_type(row):
    languages = Counter(token["gold"] for token in row["tokens"] if token["gold"] in LANGUAGES)
    if row["gold_message"] == "non_mixed":
        return next(iter(languages)) + "_only"
    if row["gold_message"] == "mixed" and min(languages.values()) == 1:
        return "one_word_switch"
    return row["gold_message"]


def policy_results(rows, summary):
    by_case_type = defaultdict(Counter)
    for row in rows:
        by_case_type[case_type(row)][row["outcome"]] += 1
    one_word = by_case_type["one_word_switch"]
    return {
        "switch": summary["switch"],
        "one_word_switches": {"support": one_word.total(), "firm_mixed": one_word["mixed"]},
        "outcomes_by_case_type": {key: dict(counts) for key, counts in by_case_type.items()},
    }


def lock(out):
    _, inputs = comparison_inputs()
    with new_artifact_dir(out) as staging:
        write_json(staging / "lock.json", {"locked_at_utc": datetime.now(timezone.utc).isoformat(), "inputs": inputs})


def score(out):
    lock_path = out / "lock.json"
    if (out / "score").exists():
        raise InputError("This comparison has already been scored.")
    model, inputs = comparison_inputs()
    if read_json(lock_path)["inputs"] != inputs:
        raise InputError("Comparison inputs differ from the lock.")
    cases = [row for row in read_rows(ANNOTATIONS) if row["split"] == inputs["split"]]
    if (len({row["message_id"] for row in cases}) != inputs["expected_messages"]
            or len(cases) != inputs["expected_messages"]
            or any(row["human_verified"] is not True or row["reviewer_ids"] != ["R1"] for row in cases)):
        raise InputError("Expected 60 distinct holdout messages confirmed by R1.")

    rows = {
        name: list(predictions(cases, model, Policy(**policy)))
        for name, policy in inputs["policies"].items()
    }
    transitions = defaultdict(Counter)
    for before, after in zip(rows["baseline"], rows["candidate"], strict=True):
        if before["message_id"] != after["message_id"] or before["tokens"] != after["tokens"]:
            raise InputError("Changing the alert cutoff changed the aligned word predictions.")
        old_outcome, new_outcome = before["outcome"], after["outcome"]
        if old_outcome != new_outcome:
            if (old_outcome, new_outcome) != ("mixed", "possible_switch"):
                raise InputError("Unexpected alert transition after raising the cutoff.")
            transitions[case_type(before)][f"{old_outcome}_to_{new_outcome}"] += 1

    summaries = {name: summarize(result, reviewed=True) for name, result in rows.items()}
    metrics = {name: policy_results(result, summaries[name]) for name, result in rows.items()}
    baseline, candidate = metrics["baseline"], metrics["candidate"]
    checks = {
        "fewer_false_mixed_alerts": candidate["switch"]["false_positive"] < baseline["switch"]["false_positive"],
        "genuine_mixed_alerts_preserved": candidate["switch"]["true_positive"] >= baseline["switch"]["true_positive"],
        "one_word_switches_preserved": candidate["one_word_switches"]["firm_mixed"]
        >= baseline["one_word_switches"]["firm_mixed"],
    }
    report = {
        "lock_sha256": file_sha(lock_path),
        "messages": len(cases),
        "word_metrics": summaries["baseline"]["tokens"],
        "policies": metrics,
        "alert_transitions": {key: dict(counts) for key, counts in transitions.items()},
        "checks": checks,
        "candidate_passed": all(checks.values()),
    }
    with new_artifact_dir(out / "score") as staging:
        write_json(staging / "metrics.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("lock", "score"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        action = {"lock": lock, "score": score}[args.phase]
        action(args.out)
        print(f"{args.phase} completed in {args.out}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"TilSwitch: {error}\n")
