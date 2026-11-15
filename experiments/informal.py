"""Lock and score a local experiment on informal spellings and switch evidence."""

import argparse
from collections import Counter
from dataclasses import replace
from pathlib import Path

from tilswitch.evaluate import _dev_support, _review_inputs, predictions, summarize
from tilswitch.model import load_bundle, save_bundle
from tilswitch.prepare import duplicate_pairs, gold_message_label, review_candidates, verified_split
from tilswitch.text import tokenize
from tilswitch.types import (
    GOLD_LABELS, LANGUAGES, InputError, RunConfig, file_sha, new_artifact_dir, read_json, read_rows, write_json,
)


CASES = Path(__file__).with_name("informal-cases.jsonl")
BUNDLES = {"current": Path("artifacts/models/krcs-release"), "augmented": Path("artifacts/models/word-informal")}
MARGINS = (0.0, 0.20, 0.35, 0.50)


def authored_cases(split):
    cases = []
    for row in read_rows(CASES):
        if row["split"] != split:
            continue
        tokens = []
        labels = iter(row["labels"])
        for token in tokenize(row["text"]):
            label = next(labels, None) if token.lexical else "neutral"
            if label not in GOLD_LABELS:
                raise InputError(f'{row["message_id"]}: missing or invalid label.')
            tokens.append({"start": token.start, "end": token.end, "text": token.text,
                           "label": label, "reason": None})
        if next(labels, None) is not None:
            raise InputError(f'{row["message_id"]}: extra word label.')
        cases.append({**row, "tokens": tokens, "message_label": gold_message_label(tokens)})
    return cases


def check_inventory(cfg):
    rows = list(read_rows(CASES))
    if len({row["message_id"] for row in rows}) != len(rows) or {row["split"] for row in rows} != {"dev", "test"}:
        raise InputError("Authored cases need unique IDs and both expected splits.")
    dev_groups, test_groups = ({row["group_id"] for row in rows if row["split"] == split} for split in ("dev", "test"))
    if dev_groups & test_groups:
        raise InputError("An authored scenario is shared between splits.")
    fixtures = [(row["message_id"], row["text"]) for row in rows]
    known = [(row["message_id"], row["text"]) for row in review_candidates(cfg, "krcs")]
    known.extend((row["message_id"], row["text"]) for row in read_rows(verified_split(cfg, "train")))
    inventory = fixtures + known
    for left, right in duplicate_pairs(inventory):
        if left < len(fixtures) or right < len(fixtures):
            raise InputError(f"An authored case duplicates another message: {inventory[left][0]}.")
    return len(fixtures)


def evaluate(cases, model):
    rows = list(predictions(cases, model, model.policy))
    report = summarize(rows, reviewed=True)
    switches = Counter()
    for row in rows:
        outcome = row["outcome"]
        if row["gold_message"] == "mixed":
            counts = Counter(token["gold"] for token in row["tokens"] if token["gold"] in LANGUAGES)
            if min(counts.values()) == 1:
                switches["one_word_support"] += 1
                switches["one_word_mixed"] += outcome == "mixed"
                switches["one_word_possible"] += outcome == "possible_switch"
            switches["mixed_as_possible"] += outcome == "possible_switch"
        elif row["gold_message"] == "non_mixed":
            switches["single_as_possible"] += outcome == "possible_switch"
    report["switch_details"] = dict(switches)
    return report


def preserves_dev(baseline, candidate):
    words = candidate["tokens"]
    reference = baseline["tokens"]
    return (words["macro_f1"] >= reference["macro_f1"]
            and words["per_label"]["kk"]["recall"] >= reference["per_label"]["kk"]["recall"]
            and words["coverage"] >= reference["coverage"]
            and candidate["switch"]["true_positive"] >= baseline["switch"]["true_positive"]
            and candidate["switch"]["false_positive"] <= baseline["switch"]["false_positive"])


def lock_candidate(output):
    cfg = RunConfig.load(Path("conf/experiment.json"))
    inventory_size = check_inventory(cfg)
    development = _review_inputs(cfg, "krcs", "dev")
    if not _dev_support(development):
        raise InputError("Validate enough bilingual development labels before locking the experiment.")
    dev_path, _, human_dev = development
    school_dev = authored_cases("dev")
    manifests = {name: file_sha(path / "manifest.json") for name, path in BUNDLES.items()}
    models = {name: load_bundle(path, manifests[name]) for name, path in BUNDLES.items()}
    train_sha = file_sha(verified_split(cfg, "train"))
    if any(read_json(path / "metadata.json")["train_sha256"] != train_sha for path in BUNDLES.values()):
        raise InputError("The two models must use the same prepared training split.")
    baseline = models["current"]
    human_reference = evaluate(human_dev, baseline)
    school_reference = evaluate(school_dev, baseline)
    trials = []
    for name, model in models.items():
        for margin in MARGINS:
            policy = replace(baseline.policy, singleton_switch_margin=margin)
            candidate = replace(model, policy=policy)
            human = evaluate(human_dev, candidate)
            school = evaluate(school_dev, candidate)
            allowed = (preserves_dev(human_reference, human)
                       and school["switch"]["true_positive"] >= school_reference["switch"]["true_positive"]
                       and school["switch_details"].get("one_word_mixed", 0)
                       >= school_reference["switch_details"].get("one_word_mixed", 0))
            trials.append({"model": name, "singleton_switch_margin": margin, "eligible": allowed,
                           "human_dev": human, "authored_dev": school})

    def selection_key(trial):
        school = trial["authored_dev"]
        return (-school["switch"]["false_positive"], school["switch"]["true_positive"],
                trial["human_dev"]["tokens"]["macro_f1"], school["tokens"]["macro_f1"],
                -trial["singleton_switch_margin"])

    chosen = max((trial for trial in trials if trial["eligible"]), key=selection_key)
    name, margin = chosen["model"], chosen["singleton_switch_margin"]
    policy = replace(baseline.policy, singleton_switch_margin=margin)
    chosen_model = replace(models[name], policy=policy)
    with new_artifact_dir(output) as staged:
        lock = staged / "lock.json"
        write_json(lock, {
            "cases_sha256": file_sha(CASES), "cases": inventory_size,
            "human_dev_sha256": file_sha(dev_path), "bundle_manifests": manifests,
            "selected_model": name, "model_id": chosen_model.model_id,
            "policy": vars(policy), "development_trials": trials,
        })
        metadata = read_json(BUNDLES[name] / "metadata.json")
        metadata["evaluation_lock_sha256"] = file_sha(lock)
        save_bundle(staged / "model", chosen_model, metadata)
    print(f"{chosen_model.model_id}, switch margin {margin:.2f}. Lock saved to {output / 'lock.json'}.")


def locked_candidate(folder):
    lock_path = folder / "lock.json"
    lock = read_json(lock_path)
    if file_sha(CASES) != lock["cases_sha256"]:
        raise InputError("The authored cases changed after the development lock.")
    models = {name: load_bundle(path, lock["bundle_manifests"][name]) for name, path in BUNDLES.items()}
    candidate = load_bundle(folder / "model")
    selected = read_json(BUNDLES[lock["selected_model"]] / "manifest.json")
    copied = read_json(folder / "model" / "manifest.json")
    if (vars(candidate.policy) != lock["policy"] or candidate.model_id != lock["model_id"]
            or any(copied[name] != selected[name] for name in ("weights.npz", "vocabulary.json"))
            or read_json(folder / "model" / "metadata.json")["evaluation_lock_sha256"] != file_sha(lock_path)):
        raise InputError("The candidate bundle does not match its development lock.")
    return lock_path, models, candidate


def score_candidate(folder):
    lock_path, models, candidate = locked_candidate(folder)
    cases = authored_cases("test")
    original = models["current"]
    scores = {
        "current": evaluate(cases, original),
        "augmentation_only": evaluate(cases, replace(models["augmented"], policy=original.policy)),
        "selected": evaluate(cases, candidate),
    }
    with new_artifact_dir(folder / "test") as output:
        write_json(output / "summary.json", {"authorship": "AI-authored and labeled", "lock_sha256": file_sha(lock_path),
                                             "messages": len(cases), "models": scores})
    print(f"Scored {len(cases)} authored cases. Summary saved to {folder / 'test' / 'summary.json'}.")


def replay_previous_sets(folder):
    output = folder / "replay.json"
    if output.exists():
        raise InputError(f"Output already exists: {output}")
    lock_path, models, candidate = locked_candidate(folder)
    cfg = RunConfig.load(Path("conf/experiment.json"))
    reviewed = _review_inputs(cfg, "krcs", "test")
    if reviewed is None:
        raise InputError("The original human-reviewed test file is needed for replay.")
    krcs_path, _, krcs = reviewed
    mono_path = verified_split(cfg, "test")
    evidence = Path("release/evidence")
    hashes = {"krcs_v1": file_sha(krcs_path), "tatoeba_v1": file_sha(mono_path)}
    for name, dataset, lock_file in (("krcs_v1", "krcs", "krcs-v1.lock.json"),
                                      ("tatoeba_v1", "mono", "mono-v1.lock.json")):
        if hashes[name] != read_json(evidence / lock_file)["test"][dataset]["sha256"]:
            raise InputError(f"The data differ from the original {name} test.")
    comparison = {"current": models["current"], "selected": candidate}
    mono = list(read_rows(mono_path))
    write_json(output, {
        "scope": "Previously evaluated sets, scored after local candidate was locked",
        "lock_sha256": file_sha(lock_path), "data_sha256": hashes,
        "datasets": {
            "krcs_v1": {key: evaluate(krcs, model) for key, model in comparison.items()},
            "tatoeba_v1": {key: summarize(list(predictions(mono, model, model.policy)), reviewed=False)
                           for key, model in comparison.items()},
        },
    })
    print(f"Replayed the previously evaluated KRCS and Tatoeba tests. Summary saved to {output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("lock", "score", "replay"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.phase == "lock":
        lock_candidate(args.out)
    elif args.phase == "score":
        score_candidate(args.out)
    else:
        replay_previous_sets(args.out)
