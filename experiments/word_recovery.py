"""Build and check word recovery using frozen Tatoeba, KRCS and FLORES sources."""

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

from .borrowing_review import RECEIPT as EARLIER_RECEIPT, document_metrics, read_external
from .informal import authored_cases, evaluate
from tilswitch.augment import INFORMAL_LETTERS
from tilswitch.evaluate import _review_inputs
from tilswitch.features import training_words
from tilswitch.infer import analyze
from tilswitch.model import Policy, load_bundle, save_bundle
from tilswitch.prepare import Groups, duplicate_pairs, review_candidates, verified_split
from tilswitch.sources import FLORES, KRCS, flores_rows, krcs_rows
from tilswitch.text import normalize_word, tokenize
from tilswitch.types import (
    LANGUAGES, InputError, RunConfig, file_sha, json_dump, new_artifact_dir, read_json, read_rows, stable_key,
    text_sha, write_json,
)
from tilswitch.word_evidence import WordEvidence


SEED = 6149
GROUP_COUNTS = {"dev": 100, "devtest": 200}
FILES_TO_LOCK = ("experiments/word_recovery.py", "tilswitch/infer.py", "tilswitch/text.py", "tilswitch/word_evidence.py")


def _terms(text):
    return {normalize_word(token.text) for token in tokenize(text)
            if token.lexical and token.reason is None and token.script == "cyrillic"}


def _parallel_words(cfg, rows):
    groups = Groups(row["message_id"] for row in rows)
    by_id = {row["message_id"]: index for index, row in enumerate(rows)}
    texts = [(row["message_id"], text) for row in rows for text in (row["text"], *row["translations"])]
    for left, right in duplicate_pairs(texts):
        groups.merge(by_id[texts[left][0]], by_id[texts[right][0]])
    reserved = {groups.name(by_id[row["message_id"]]) for row in review_candidates(cfg, "krcs")}
    kazakh = Counter()
    russian = set()
    support = 0
    seen_groups = set()
    for index, row in enumerate(rows):
        group = groups.name(index)
        if group in reserved or group in seen_groups:
            continue
        seen_groups.add(group)
        kk, ru = (_terms(text) for text in row["translations"])
        original = _terms(row["text"])
        folded = {word.translate(INFORMAL_LETTERS) for word in kk}
        kazakh_only = original & ((kk | folded) - ru)
        kazakh.update(kazakh_only)
        russian.update(ru)
        support += bool(kazakh_only)
    return kazakh, russian, support


def _spellings(cfg, training, krcs):
    natural, russian, support = _parallel_words(cfg, krcs)
    folded = Counter()
    for label, row in training_words(training, cfg):
        if label == "ru":
            russian.add(row.surface)
        elif label == "kk":
            spelling = row.surface.translate(INFORMAL_LETTERS)
            if spelling != row.surface:
                folded[spelling] += 1
    for word, count in natural.items():
        spelling = word.translate(INFORMAL_LETTERS)
        if spelling != word:
            folded[spelling] += count
    aliases = frozenset(word for word, count in folded.items() if count >= 2 and word not in russian)
    strong = frozenset(word for word in aliases if natural[word] >= 2)
    return WordEvidence(aliases, strong), {
        "parallel_groups_with_weak_kazakh_labels": support,
        "eligible_folded_spellings": len(aliases),
        "parallel_spellings": len(strong),
    }


def _fragments(inventory, known, split):
    originals = defaultdict(dict)
    for row in inventory:
        key = row["upstream_group"]
        if row["upstream_split"] == split:
            originals[key][row["source_lang"]] = row["text"]
        if split == "devtest" and row["upstream_split"] == "dev":
            known.append((key, row["text"]))
    texts = [(key, text) for key, group in originals.items() for text in group.values()]
    start = len(known)
    excluded = {texts[right - start][0] for left, right in duplicate_pairs(known + texts) if left < start <= right}
    cases = []
    order = sorted(originals, key=lambda key: (stable_key(SEED, key), key))
    for key in order:
        if key in excluded:
            continue
        windows = {}
        for language, text in originals[key].items():
            script = "latin" if language == "en" else "cyrillic"
            words = [token.text for token in tokenize(text) if token.lexical and token.script == script
                     and token.reason in {None, "short_word"}]
            if len(words) >= 6:
                start_word = stable_key(SEED, key + language) % (len(words) - 5)
                windows[language] = words[start_word:start_word + 6]
        if set(windows) != set(LANGUAGES):
            continue
        kk, ru, en = (windows[language] for language in LANGUAGES)
        kk_words, ru_words = ({normalize_word(word) for word in group} for group in (kk, ru))
        kk_donors = [word for word in kk if len(word) >= 2 and normalize_word(word) not in ru_words]
        ru_donors = [word for word in ru if len(word) >= 2 and normalize_word(word) not in kk_words]
        folded = [word.casefold().translate(INFORMAL_LETTERS) for word in kk]
        if not kk_donors or not ru_donors or folded == [word.casefold() for word in kk]:
            continue
        ru_word = ru_donors[stable_key(SEED, key + "r") % len(ru_donors)]
        kk_word = kk_donors[stable_key(SEED, key + "k") % len(kk_donors)]
        for name, terms, labels in (
            ("standard_kk", kk, ["kk"] * 6),
            ("unaccented_kk", folded, ["kk"] * 6),
            ("russian", ru, ["ru"] * 6),
            ("english", en, ["en"] * 6),
            ("kk_with_ru", kk[:3] + [ru_word] + kk[3:], ["kk"] * 3 + ["ru"] + ["kk"] * 3),
            ("ru_with_kk", ru[:3] + [kk_word] + ru[3:], ["ru"] * 3 + ["kk"] + ["ru"] * 3),
        ):
            cases.append({"group": key, "slice": name, "text": " ".join(terms), "labels": labels})
        if len(cases) == GROUP_COUNTS[split] * 6:
            break
    if len(cases) != GROUP_COUNTS[split] * 6:
        raise InputError(f"Insufficient eligible paired FLORES groups for {split}.")
    return cases


def _stress_scores(cases, model):
    slices = defaultdict(Counter)
    for case in cases:
        result = analyze(case["text"], model)
        labels = [token["label"] for token in result["tokens"]]
        gold = case["labels"]
        counts = slices[case["slice"]]
        counts["messages"] += 1
        counts["words"] += len(gold)
        counts["correct"] += sum(expected == found for expected, found in zip(gold, labels, strict=True))
        counts["assigned"] += sum(label in LANGUAGES for label in labels)
        counts["firm_mixed"] += result["status"] == "mixed"
        if len(gold) == 7:
            counts["insertion_correct"] += labels[3] == gold[3]
    return {key: dict(counts) for key, counts in slices.items()}


def _review_scores(cases, model):
    result = evaluate(cases, model)
    return {**{key: result["tokens"][key] for key in ("macro_f1", "coverage", "units", "accepted", "accepted_error")},
            "messages": result["switch"], "one_word": result["switch_details"]}


def _gate(reference, candidate):
    old, new = reference["flores"], candidate["flores"]
    old_doc, new_doc = reference["kaznlp"]["all"], candidate["kaznlp"]["all"]
    missed_words = ("russian", "english")
    mixed = ("kk_with_ru", "ru_with_kk")
    return {
        "unaccented_words_improved": new["unaccented_kk"]["correct"] > old["unaccented_kk"]["correct"],
        "russian_and_english_words_preserved": all(new[key]["correct"] >= old[key]["correct"] for key in missed_words),
        "synthetic_insertions_preserved": all(new[key]["insertion_correct"] >= old[key]["insertion_correct"] for key in mixed),
        "reviewed_coverage_preserved": candidate["krcs"]["coverage"] >= reference["krcs"]["coverage"],
        "reviewed_word_f1_preserved": candidate["krcs"]["macro_f1"] >= reference["krcs"]["macro_f1"],
        "reviewed_switches_preserved": candidate["krcs"]["messages"]["true_positive"] >= reference["krcs"]["messages"]["true_positive"],
        "reviewed_false_flags_preserved": candidate["krcs"]["messages"]["false_positive"] <= reference["krcs"]["messages"]["false_positive"],
        "reviewed_one_word_switches_preserved": candidate["krcs"]["one_word"]["one_word_mixed"] >= reference["krcs"]["one_word"]["one_word_mixed"],
        "document_russian_false_flags_preserved": new_doc["ru"].get("mixed", 0) <= old_doc["ru"].get("mixed", 0),
        "document_clause_switches_preserved": new_doc["mixed"].get("mixed", 0) >= old_doc["mixed"].get("mixed", 0),
    }


def run(phase, output, baseline, kaznlp_folder):
    cfg = RunConfig.load(Path("conf/experiment.json"))
    earlier = read_json(EARLIER_RECEIPT)
    original = load_bundle(baseline, earlier["baseline_bundle"])
    old = replace(original, policy=Policy(**earlier["inference_policy"]))
    train_path = verified_split(cfg, "train")
    training = list(read_rows(train_path))
    krcs = list(krcs_rows(cfg.raw / KRCS.name))
    if file_sha(cfg.raw / FLORES.name) != FLORES.sha256:
        raise InputError("FLORES archive differs from the pinned source.")
    inventory = list(flores_rows(cfg.raw / FLORES.name))
    known = [(row["message_id"], row["text"]) for row in training]
    known.extend((row["message_id"], text) for row in krcs for text in (row["text"], *row["translations"]))
    cases = {split: _fragments(inventory, known.copy(), split) for split in GROUP_COUNTS}
    word_evidence, support = _spellings(cfg, training, krcs)
    evidence_hash = text_sha(json_dump(word_evidence.to_json()))
    lock = {
        "training_sha256": file_sha(train_path), "krcs_sha256": KRCS.sha256, "flores_sha256": FLORES.sha256,
        "case_sha256": {key: text_sha(json_dump(data)) for key, data in cases.items()},
        "word_evidence_sha256": evidence_hash, "word_evidence_support": support,
        "code_sha256": {path: text_sha(Path(path).read_text(encoding="utf-8")) for path in FILES_TO_LOCK},
        "baseline_manifest_sha256": earlier["baseline_bundle"], "policy": earlier["inference_policy"],
        "reviewed_replay_sha256": earlier["results"]["test"]["krcs_sha256"],
        "kaznlp_replay_sha256": earlier["results"]["test"]["kaznlp_sha256"],
        "school_fixtures_sha256": earlier["fixtures_sha256"],
    }
    if file_sha(Path("experiments/informal-cases.jsonl")) != lock["school_fixtures_sha256"]:
        raise InputError("The scripted review inventory changed.")
    lock_path = output / "lock.json"
    if phase == "score" and read_json(lock_path) != lock:
        raise InputError("The data, code or selected spellings changed after the lock.")
    split, local_split = ("dev", "dev") if phase == "lock" else ("devtest", "test")
    reviewed = _review_inputs(cfg, "krcs", local_split)
    if reviewed is None:
        raise InputError("The validated KRCS review files are required.")
    earlier_result = earlier["results"]["development" if phase == "lock" else "test"]
    if file_sha(reviewed[0]) != earlier_result["krcs_sha256"]:
        raise InputError("KRCS reference labels differ from the original evaluation.")
    external = read_external(kaznlp_folder, "val" if phase == "lock" else "test", earlier_result["kaznlp_sha256"])
    candidate = replace(old, model_id="word-recovery-" + evidence_hash[:10], word_evidence=word_evidence)
    if phase == "score":
        bundle = output / "model"
        measured = load_bundle(bundle)
        manifest = read_json(bundle / "manifest.json")
        baseline_manifest = read_json(baseline / "manifest.json")
        metadata = read_json(bundle / "metadata.json")
        if (measured.model_id != candidate.model_id or measured.word_evidence != word_evidence
                or measured.policy != old.policy or metadata["word_recovery_lock_sha256"] != file_sha(lock_path)
                or any(manifest[name] != baseline_manifest[name] for name in ("weights.npz", "vocabulary.json"))):
            raise InputError("The staged bundle differs from the locked word evidence.")
        candidate = measured
    scores = {key: {
        "flores": _stress_scores(cases[split], model),
        "krcs": _review_scores(reviewed[2], model),
        "scripted": _review_scores(authored_cases(local_split), model),
        "kaznlp": document_metrics(external, model),
    } for key, model in (("prior", old), ("candidate", candidate))}
    gate = _gate(scores["prior"], scores["candidate"])
    report = {"phase": phase, "flores_groups": GROUP_COUNTS[split], "gate": gate,
              "lock_sha256": text_sha(json_dump(lock)), "scores": scores}
    if phase == "lock":
        with new_artifact_dir(output) as directory:
            write_json(directory / "lock.json", lock)
            write_json(directory / "development.json", report)
            metadata = read_json(baseline / "metadata.json")
            metadata["word_recovery_lock_sha256"] = file_sha(directory / "lock.json")
            save_bundle(directory / "model", candidate, metadata)
    else:
        with new_artifact_dir(output / "test") as directory:
            write_json(directory / "summary.json", report)
    print(json_dump({"phase": phase, "gate": gate, "spellings": support, "output": str(output)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("lock", "score"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=Path("artifacts/models/krcs-release"))
    parser.add_argument("--kaznlp-dir", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        run(arguments.phase, arguments.out, arguments.baseline, arguments.kaznlp_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f"TilSwitch: {error}\n")
