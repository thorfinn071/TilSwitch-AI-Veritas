from dataclasses import replace
from pathlib import Path

import pytest

from tilswitch.evaluate import classify_metrics, create_lock, evaluate_test, make_release, summarize
from tilswitch.infer import analyze
from tilswitch.model import load_bundle
from tilswitch.prepare import _candidate_hash, review_candidates
from tilswitch.text import tokenize
from tilswitch.train import train
from tilswitch.types import InputError, RunConfig, file_sha, write_json, write_rows

TEXT = {
    "kk": ["Сәлем достар", "Бүгін сабақ болады", "Қазақша сөйлесейік"],
    "ru": ["Добрый вечер", "Завтра урок начинается", "Увидимся после уроков"],
    "en": ["Hello everyone", "Bring your notebook", "See you tomorrow"],
}


def _fixture_rows(split):
    return [{"message_id": f"{split}-{label}-{index}", "group_id": f"{split}-{label}-{index}",
             "source_lang": label, "text": text}
            for label, items in TEXT.items() for index, text in enumerate(items)]


def test_abstention_counts_as_error_and_absent_class_is_unavailable():
    results = classify_metrics([("kk", "kk"), ("kk", "unk"), ("ru", "ru"), ("ru", "kk")],
                               ("kk", "ru", "en"), ("kk", "ru", "en", "unk"))
    assert results["accuracy"] == 0.5
    assert results["per_label"]["kk"]["recall"] == 0.5
    assert results["per_label"]["ru"]["precision"] == 1
    assert results["per_label"]["en"]["f1"] is None
    assert results["macro_f1"] is None
    assert results["confusion"]["kk"]["unk"] == 1


def test_switch_scores_treat_review_as_negative_and_exclude_indeterminate():
    rows = [{"gold_message": gold, "outcome": predicted, "short": True, "tokens": []}
            for gold, predicted in [("mixed", "mixed"), ("mixed", "needs_review"),
                                    ("non_mixed", "mixed"), ("non_mixed", "kk"),
                                    ("indeterminate", "mixed")]]
    result = summarize(rows, reviewed=True)["switch"]
    assert result["precision"] == result["recall"] == 0.5
    assert result["review_outcomes"] == result["indeterminate_or_neutral"] == 1


def test_train_lock_score_release_and_digest_guards(tmp_path):
    cfg = replace(RunConfig.load(Path("conf/experiment.json")),
                  data_dir=tmp_path / "data", artifact_dir=tmp_path / "artifacts")
    hashes = {}
    for split in ("train", "dev", "test"):
        path = cfg.prepared / f"{split}.jsonl"
        write_rows(path, _fixture_rows(split))
        hashes[split] = file_sha(path)
    candidates = cfg.review / "authored-candidates.jsonl"
    write_rows(candidates, [
        {"message_id": "test-example", "family_id": "fixture-mixed", "split": "test",
         "text": "Сәлем, завтра!"},
    ])
    example, = review_candidates(cfg, "authored")
    inventory = _candidate_hash([example])
    gold_path = cfg.review / "authored-test.gold.jsonl"
    gold_tokens = [{**vars(token), "label": {"Сәлем": "kk", "завтра": "ru"}.get(token.text, "neutral")}
                   for token in tokenize(example["text"])]
    write_rows(gold_path, [{**example, "tokens": gold_tokens, "message_label": "mixed"}])
    write_json(gold_path.with_suffix(".json"), {
        "dataset": "authored", "split": "test", "gold_sha256": file_sha(gold_path), "inventory_id": inventory,
        "messages": 1, "short_messages": 1, "label_counts": {"kk": 1, "ru": 1}, "label_messages": {"kk": 1, "ru": 1},
    })
    write_json(cfg.prepared / "manifest.json", {"split_sha256": hashes, "review_inventory": {"team": inventory}})
    for mode in ("word", "context"):
        bundle, _ = train(cfg, mode)
        model = load_bundle(bundle)
        assert set(model.classes) == set(TEXT)
        assert analyze("Сәлем, hello!", model) == analyze("Сәлем, hello!", model)
    lock_path = cfg.runs / "test.lock.json"
    lock = create_lock(cfg, lock_path, ("mono", "authored"))
    assert lock["release_model"] == "word"
    result = evaluate_test(cfg, lock_path, cfg.runs / "test")
    assert result["datasets"]["mono"]["models"]["word"]["base"]["messages"] == 9
    assert result["datasets"]["authored"]["models"]["heuristic"]["base"]["tokens"]["macro_f1"] == 1.0
    assert result["datasets"]["authored"]["models"]["word"]["base"]["switch_boundary_tokens"]["units"] == 2
    assert not result["datasets"]["authored"]["supports_primary"]
    assert (cfg.runs / "test" / "per_language.csv").is_file()
    release = cfg.models / "release"
    make_release(cfg, lock_path, release)
    assert analyze("Hello everyone!", load_bundle(release))["model_id"].startswith("word-")
    with pytest.raises(InputError, match="exists"):
        evaluate_test(cfg, lock_path, cfg.runs / "test")
    (cfg.prepared / "test.jsonl").write_text("{}", encoding="utf-8")
    with pytest.raises(InputError, match="differs"):
        evaluate_test(cfg, lock_path, cfg.runs / "changed-test")
    assert not (cfg.runs / "changed-test").exists()
    (release / "policy.json").write_text("{}", encoding="utf-8")
    with pytest.raises(InputError, match="checksum"):
        load_bundle(release)
