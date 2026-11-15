from __future__ import annotations

import csv
from collections import Counter
from dataclasses import replace
from pathlib import Path
from statistics import median
from time import perf_counter

from .infer import analyze
from .model import Policy, load_bundle, save_bundle
from .prepare import review_candidates, verified_split
from .text import KAZAKH_LETTERS, context_indices, normalize_word, tokenize
from .types import (
    LANGUAGES, SCHEMA, InputError, RunConfig, atomic_text, file_sha, new_artifact_dir,
    read_json, read_rows, write_json, write_rows,
)

MONO_OUTCOMES = (*LANGUAGES, "mixed", "needs_review", "neutral_only")
REVIEW_DATASETS = ("krcs", "authored")
REVIEW_CASES = ("ambiguous", "other", "unknown", "neutral")


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def classify_metrics(pairs, labels: tuple[str, ...], outcomes: tuple[str, ...]) -> dict:
    counts = Counter(pairs)
    total = sum(counts.values())
    per_label = {}
    for label in labels:
        true_positive = counts[label, label]
        support = sum(n for (actual, _), n in counts.items() if actual == label)
        predicted = sum(n for (_, model), n in counts.items() if model == label)
        per_label[label] = {
            "precision": _ratio(true_positive, predicted),
            "recall": _ratio(true_positive, support),
            "f1": _ratio(2 * true_positive, support + predicted) if support else None,
            "support": support, "predicted": predicted, "correct": true_positive,
        }
    scores = [row["f1"] for row in per_label.values()]
    return {"units": total, "accuracy": _ratio(sum(n for (a, b), n in counts.items() if a == b), total),
            "macro_f1": sum(scores) / len(scores) if all(score is not None for score in scores) else None,
            "per_label": per_label,
            "confusion": {label: {outcome: counts[label, outcome] for outcome in outcomes} for label in labels}}


def _aligned(case: dict, result: dict) -> list[dict]:
    rows = []
    if "tokens" in case:
        gold = case["tokens"]
        context = context_indices(case["text"], tokenize(case["text"]))
        if len(gold) != len(result["tokens"]):
            raise InputError(f'Gold token count differs: {case["message_id"]}')
        for index, (actual, predicted) in enumerate(zip(gold, result["tokens"], strict=True)):
            if any(actual[field] != predicted[field] for field in ("start", "end", "text")):
                raise InputError(f'Gold offsets differ: {case["message_id"]}')
            adjacent = [gold[position]["label"] for position in context[index] if position is not None]
            boundary = any(label in LANGUAGES and label != actual["label"] for label in adjacent)
            rows.append({"start": actual["start"], "end": actual["end"], "gold": actual["label"],
                         "gold_reason": actual["reason"], "label": predicted["label"],
                         "reason": predicted["reason"], "adjacent_switch": boundary,
                         "kazakh_marked": bool(KAZAKH_LETTERS.intersection(normalize_word(actual["text"])))})
    else:
        for predicted in result["tokens"]:
            if predicted["label"] == "neutral":
                continue
            rows.append({"start": predicted["start"], "end": predicted["end"], "gold": case["source_lang"],
                         "label": predicted["label"], "reason": predicted["reason"],
                         "kazakh_marked": bool(KAZAKH_LETTERS.intersection(normalize_word(predicted["text"])))})
    return rows


def predictions(cases, model, policy: Policy):
    for case in cases:
        result = analyze(case["text"], model, policy)
        yield {"message_id": case["message_id"], "group_id": case["group_id"],
               "gold_message": case.get("message_label") or case["source_lang"],
               "outcome": result["primary_language"] or result["status"],
               "short": result["lexical_count"] <= 5, "tokens": _aligned(case, result)}


def _token_scores(rows, labels):
    pairs = [(token["gold"], token["label"]) for row in rows for token in row["tokens"]
             if token["gold"] in labels]
    metrics = classify_metrics(pairs, labels, (*LANGUAGES, "unk", "neutral"))
    accepted = [(gold, label) for gold, label in pairs if label in LANGUAGES]
    metrics.update({"accepted": len(accepted),
                    "coverage": _ratio(len(accepted), len(pairs)),
                    "accepted_error": _ratio(sum(gold != label for gold, label in accepted), len(accepted))})
    return metrics


def _switch_scores(rows):
    resolved = [row for row in rows if row["gold_message"] in {"mixed", "non_mixed"}]
    counts = Counter((row["gold_message"] == "mixed", row["outcome"] == "mixed") for row in resolved)
    tp, fp, fn, tn = counts[True, True], counts[False, True], counts[True, False], counts[False, False]
    precision = _ratio(tp, tp + fp) if tp + fn and fp + tn else None
    recall = _ratio(tp, tp + fn)
    return {"true_positive": tp, "false_positive": fp, "false_negative": fn, "true_negative": tn,
            "precision": precision, "recall": recall,
            "f1": _ratio(2 * tp, 2 * tp + fp + fn) if tp + fn and fp + tn else None,
            "review_outcomes": sum(row["outcome"] in {"needs_review", "possible_switch"} for row in resolved),
            "resolved": len(resolved), "indeterminate_or_neutral": len(rows) - len(resolved)}


def summarize(rows: list[dict], reviewed: bool) -> dict:
    labels = ("kk", "ru") if reviewed else LANGUAGES
    short = [row for row in rows if row["short"]]
    kk_by_spelling = {}
    for flag, name in ((False, "no_distinctive_letters"), (True, "has_distinctive_letters")):
        words_by_message = [
            [(token["gold"], token["label"]) for token in row["tokens"]
             if token["gold"] == "kk" and token["kazakh_marked"] == flag] for row in rows
        ]
        words = [label for group in words_by_message for _, label in group]
        kk_by_spelling[name] = {"tokens": len(words), "messages": sum(bool(group) for group in words_by_message),
                                "recall": _ratio(words.count("kk"), len(words))}
    summary = {"messages": len(rows), "short_messages": len(short), "tokens": _token_scores(rows, labels),
               "short_tokens": _token_scores(short, labels), "kazakh_spelling": kk_by_spelling}
    if reviewed:
        summary["switch"] = _switch_scores(rows)
        summary["switch_boundary_tokens"] = _token_scores(
            [{"tokens": [token for token in row["tokens"] if token.get("adjacent_switch")]} for row in rows], labels
        )
        summary["other_tokens"] = _token_scores(
            [{"tokens": [token for token in row["tokens"] if not token.get("adjacent_switch")]} for row in rows], labels
        )
        summary["excluded_gold"] = {
            label: dict(Counter(token["label"] for row in rows for token in row["tokens"] if token["gold"] == label))
            for label in (*REVIEW_CASES, "en")
        }
        lexical_resolved = [
            [token for token in row["tokens"] if token["gold"] != "neutral"] for row in rows
            if row["gold_message"] in {"mixed", "non_mixed"}
            and all(token["gold"] not in REVIEW_CASES[:3] for token in row["tokens"])
        ]
        summary["exact_message_match"] = {
            "eligible": len(lexical_resolved),
            "matched": sum(all(token["gold"] == token["label"] for token in row) for row in lexical_resolved),
        }
    else:
        outcomes = MONO_OUTCOMES
        if any(row["outcome"] == "possible_switch" for row in rows):
            outcomes = (*outcomes, "possible_switch")
        summary["sentence_outcomes"] = classify_metrics(((row["gold_message"], row["outcome"]) for row in rows),
                                                       LANGUAGES, outcomes)
        summary["short_sentence_outcomes"] = classify_metrics(
            ((row["gold_message"], row["outcome"]) for row in short), LANGUAGES, outcomes
        )
    return summary


def _review_inputs(cfg: RunConfig, dataset: str, split: str):
    path = cfg.review / f"{dataset}-{split}.gold.jsonl"
    if not path.is_file():
        return None
    receipt = read_json(path.with_suffix(".json"))
    prepared = read_json(cfg.prepared / "manifest.json")
    location = "team" if dataset == "authored" else dataset
    candidates = [row for row in review_candidates(cfg, dataset) if row["split"] == split]
    if (receipt["dataset"] != dataset or receipt["split"] != split
            or receipt["gold_sha256"] != file_sha(path)
            or receipt["inventory_id"] != prepared["review_inventory"].get(location)):
        raise InputError(f"The {dataset} {split} gold does not match the prepared experiment.")
    cases = list(read_rows(path))
    if [(x["message_id"], x["text_sha256"]) for x in cases] != [
        (x["message_id"], x["text_sha256"]) for x in candidates
    ]:
        raise InputError(f"Review rows changed for {dataset} {split}.")
    return path, receipt, cases


def _dev_support(entry):
    return entry is not None and entry[1]["messages"] >= 12 and all(
        entry[1]["label_messages"].get(label, 0) >= 4 for label in ("kk", "ru")
    )


def _test_support(dataset, receipt) -> bool:
    minimum = 36 if dataset == "krcs" else 30
    short = receipt["short_messages"] >= 12 if dataset == "krcs" else True
    return receipt["messages"] >= minimum and short and all(
        receipt["label_messages"].get(label, 0) >= 8 and receipt["label_counts"].get(label, 0) >= 30
        for label in ("kk", "ru")
    )


def _bundle_inventory(cfg: RunConfig):
    train_hash = file_sha(verified_split(cfg, "train"))
    models = {"heuristic": None}
    artifacts = {}
    for name in ("word", "context"):
        folder = cfg.models / name
        if not folder.is_dir():
            continue
        manifest = folder / "manifest.json"
        digest = file_sha(manifest)
        models[name] = load_bundle(folder, digest)
        if read_json(folder / "metadata.json")["train_sha256"] != train_hash:
            raise InputError(f"{name} model and prepared training split differ.")
        artifacts[name] = {"model_id": models[name].model_id, "manifest_sha256": digest}
    if "word" not in models:
        raise InputError("Train the word model before evaluation.")
    return models, artifacts


def select_dev(cfg: RunConfig):
    models, artifacts = _bundle_inventory(cfg)
    mono = list(read_rows(verified_split(cfg, "dev")))
    available = {dataset: _review_inputs(cfg, dataset, "dev") for dataset in REVIEW_DATASETS}
    chosen = next((dataset for dataset, entry in available.items() if _dev_support(entry)), None)
    authored_entry = available["authored"]
    controls = authored_entry[2] if authored_entry else []
    dev_cases = available[chosen][2] if chosen else []
    dev = {}
    policies = {}
    for name, model in models.items():
        mono_prediction = list(predictions(mono, model, Policy()))
        entry = {"mono_base": summarize(mono_prediction, reviewed=False)}
        thresholds = cfg.thresholds if chosen and model else (0.0,)
        threshold_scores = []
        for threshold in thresholds:
            policy = Policy(threshold)
            informal = summarize(list(predictions(dev_cases, model, policy)), reviewed=True) if dev_cases else None
            switch = _switch_scores(list(predictions(controls, model, policy))) if controls else None
            threshold_scores.append({"threshold": threshold, "reviewed": informal, "authored_switch": switch})
        selected = max(threshold_scores, key=lambda option: (
            option["reviewed"]["tokens"]["macro_f1"] if option["reviewed"] else 0,
            -option["authored_switch"]["false_positive"] if option["authored_switch"] else 0,
            option["reviewed"]["tokens"]["coverage"] if option["reviewed"] else 0, -option["threshold"],
        ))
        entry["thresholds"] = threshold_scores
        entry["selected_threshold"] = selected["threshold"]
        dev[name] = entry
        policies[name] = {"threshold": selected["threshold"], "mixed_review_recommended": True}
    release = "word"
    if chosen and "context" in models:
        base_word = dev["word"]["thresholds"][0]["reviewed"]["tokens"]
        base_context = dev["context"]["thresholds"][0]["reviewed"]["tokens"]
        selected = {name: next(item["reviewed"]["tokens"] for item in dev[name]["thresholds"]
                               if item["threshold"] == policies[name]["threshold"]) for name in ("word", "context")}
        if (base_context["macro_f1"] > base_word["macro_f1"]
                and selected["context"]["per_label"]["kk"]["recall"] >= selected["word"]["per_label"]["kk"]["recall"]
                and selected["context"]["coverage"] >= selected["word"]["coverage"]):
            release = "context"
    if controls:
        baseline = _switch_scores(list(predictions(controls, None, Policy())))
        for name, model in models.items():
            row = _switch_scores(list(predictions(controls, model, Policy(policies[name]["threshold"]))))
            eligible = row["true_positive"] + row["false_negative"] >= 6 and row["false_positive"] + row["true_negative"] >= 6
            if eligible and row["false_positive"] <= baseline["false_positive"] and row["true_positive"] > 0:
                policies[name]["mixed_review_recommended"] = row["recall"] < baseline["recall"]
    return {"schema_version": SCHEMA, "source_set": cfg.source_set, "informal_dev": chosen,
            "models": artifacts, "dev": dev, "release_model": release, "policies": policies,
            "dev_gold_sha256": {dataset: entry[1]["gold_sha256"] for dataset, entry in available.items() if entry},
            "prepared_manifest_sha256": file_sha(cfg.prepared / "manifest.json")}


def evaluate_dev(cfg: RunConfig, path: Path) -> dict:
    result = select_dev(cfg)
    write_json(path, result)
    return result


def create_lock(cfg: RunConfig, path: Path, datasets: tuple[str, ...]) -> dict:
    if path.exists():
        raise InputError(f"Evaluation lock already exists: {path}")
    dev = select_dev(cfg)
    if not datasets or any(dataset not in ("mono", *REVIEW_DATASETS) for dataset in datasets):
        raise InputError("Select at least one known test dataset.")
    anchors = {}
    for dataset in datasets:
        if dataset == "mono":
            anchors[dataset] = {"sha256": file_sha(verified_split(cfg, "test")), "supports_primary": True}
            continue
        gold = _review_inputs(cfg, dataset, "test")
        if gold is None:
            raise InputError(f"Validate the {dataset} test review before locking evaluation.")
        anchors[dataset] = {"sha256": gold[1]["gold_sha256"],
                            "supports_primary": _test_support(dataset, gold[1]), "receipt": gold[1]}
    lock = {**dev, "test": anchors}
    write_json(path, lock)
    return lock


def _verify_lock(cfg: RunConfig, path: Path):
    lock = read_json(path)
    if (lock["schema_version"] != SCHEMA or cfg.source_set != lock["source_set"]
            or file_sha(cfg.prepared / "manifest.json") != lock["prepared_manifest_sha256"]):
        raise InputError("Prepared source or configuration differs from the evaluation lock.")
    for dataset, digest in lock["dev_gold_sha256"].items():
        entry = _review_inputs(cfg, dataset, "dev")
        if entry is None or entry[1]["gold_sha256"] != digest:
            raise InputError(f"{dataset} development labels changed after the lock.")
    models = {"heuristic": None}
    for name, receipt in lock["models"].items():
        if name not in {"word", "context"}:
            raise InputError("Unknown candidate in evaluation lock.")
        models[name] = load_bundle(cfg.models / name, receipt["manifest_sha256"])
    return lock, models


def _metrics_csv(path: Path, report: dict):
    columns = ("dataset", "model", "policy", "slice", "unit", "label", "support", "precision", "recall", "f1")
    with atomic_text(path) as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        for dataset, dataset_result in report.items():
            for model, model_result in dataset_result["models"].items():
                for policy, results in model_result.items():
                    for slice_name, key, unit in (("all", "tokens", "word"), ("short", "short_tokens", "word"),
                                                  ("switch_edge", "switch_boundary_tokens", "word"),
                                                  ("away_from_switch", "other_tokens", "word"),
                                                  ("all", "sentence_outcomes", "message"),
                                                  ("short", "short_sentence_outcomes", "message")):
                        if key not in results:
                            continue
                        for label, metrics in results[key]["per_label"].items():
                            writer.writerow((dataset, model, policy, slice_name, unit, label,
                                             *(metrics[field] for field in columns[-4:])))


def evaluate_test(cfg: RunConfig, lock_path: Path, output: Path) -> dict:
    lock, models = _verify_lock(cfg, lock_path)
    report = {}
    with new_artifact_dir(output) as folder:
        for dataset, anchor in lock["test"].items():
            reviewed = dataset != "mono"
            if reviewed:
                gold = _review_inputs(cfg, dataset, "test")
                if gold is None:
                    raise InputError(f"Missing {dataset} gold after the lock.")
                path, _, cases = gold
            else:
                path = verified_split(cfg, "test")
                cases = list(read_rows(path))
            if file_sha(path) != anchor["sha256"]:
                raise InputError(f"{dataset} test changed after locking.")
            model_results = {}
            for name, model in models.items():
                selected = Policy(**lock["policies"][name])
                variants = {"base": Policy(0.0, selected.mixed_review_recommended)}
                if selected.threshold:
                    variants["policy"] = selected
                model_results[name] = {}
                for tag, policy in variants.items():
                    result = list(predictions(cases, model, policy))
                    write_rows(folder / f"{dataset}-{name}-{tag}.predictions.jsonl", result)
                    model_results[name][tag] = summarize(result, reviewed)
            base_scores = {name: variants["base"]["tokens"]["macro_f1"] for name, variants in model_results.items()}
            comparisons = (("word", "heuristic"), ("context", "word"), ("context", "heuristic"))
            deltas = {f"{first}_minus_{second}": base_scores[first] - base_scores[second]
                      for first, second in comparisons
                      if base_scores.get(first) is not None and base_scores.get(second) is not None}
            report[dataset] = {"supports_primary": anchor["supports_primary"], "test_sha256": anchor["sha256"],
                               "models": model_results, "base_macro_f1_deltas": deltas}
        result = {"schema_version": SCHEMA, "source_set": cfg.source_set, "lock_sha256": file_sha(lock_path),
                  "release_model": lock["release_model"], "informal_dev": lock["informal_dev"], "datasets": report}
        write_json(folder / "summary.json", result)
        _metrics_csv(folder / "per_language.csv", report)
    return result


def make_release(cfg: RunConfig, lock_path: Path, output: Path) -> dict:
    lock, models = _verify_lock(cfg, lock_path)
    chosen = lock["release_model"]
    model = replace(models[chosen], policy=Policy(**lock["policies"][chosen]))
    metadata = read_json(cfg.models / chosen / "metadata.json")
    metadata["evaluation_lock_sha256"] = file_sha(lock_path)
    save_bundle(output, model, metadata)
    return {"model_id": model.model_id, "mode": chosen, "bundle": str(output),
            "manifest_sha256": file_sha(output / "manifest.json"), "policy": lock["policies"][chosen]}


def benchmark(model, messages) -> dict:
    messages = list(messages)
    if not messages:
        raise InputError("Benchmark requires at least one message.")
    analyze(messages[0], model)
    elapsed = []
    for message in messages:
        started = perf_counter()
        analyze(message, model)
        elapsed.append(1000 * (perf_counter() - started))
    elapsed.sort()
    return {"messages": len(elapsed), "median_ms": median(elapsed),
            "p95_ms": elapsed[max(0, (95 * len(elapsed) + 99) // 100 - 1)]}
