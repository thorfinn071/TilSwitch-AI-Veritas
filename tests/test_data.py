from collections import Counter
from dataclasses import replace
from pathlib import Path
import bz2
import csv

import pytest

from tilswitch.prepare import canonical, duplicate_pairs, export_review, gold_message_label, validate_review
from tilswitch.sources import Source, _fetch, tatoeba_links, tatoeba_rows
from tilswitch.types import InputError, RunConfig, file_sha, read_rows, write_rows

CONFIG = Path("conf/experiment.json")


def test_duplicate_detection_and_distinct_short_messages():
    items = [
        ("1", "Deadline is on Thursday at 10 in the library"),
        ("2", "Deadline  is on Thursday at 12 in the library"),
        ("3", "Deadline is on Tuesday at 12 in the library"),
        ("4", "да"),
        ("5", "нет"),
    ]
    pairs = set(duplicate_pairs(items))
    assert (0, 1) in pairs
    assert (3, 4) not in pairs
    assert canonical("  СӘЛЕМ \t  бәріне  ") == "сәлем бәріне"


def test_source_formats(tmp_path):
    source = tmp_path / "sentences.bz2"
    source.write_bytes(bz2.compress("1\tkaz\tСәлем бәріне\tname\t2000\t2001\n2\teng\tHello\tname\t2000\t2001\n"
                                   "invalid\n".encode("utf-8")))
    drops = Counter()
    rows = list(tatoeba_rows(source, "kaz", drops))
    assert rows[0]["source_lang"] == "kk"
    assert "owner" not in rows[0]
    assert drops["bad_tatoeba_row"] == 2

    source.write_bytes(bz2.compress(b"1\t45\n"))
    assert list(tatoeba_links(source)) == [("tatoeba-1", "tatoeba-45")]
    source.write_bytes(bz2.compress(b"1\t45\textra\n"))
    with pytest.raises(InputError, match="translation-link"):
        list(tatoeba_links(source))


def test_fetch_rejects_a_changed_cached_payload(tmp_path):
    upstream = tmp_path / "upstream.txt"
    upstream.write_text("test data", encoding="utf-8")
    cache = tmp_path / "cache"
    cache.mkdir()
    source = Source("source.txt", upstream.as_uri(), "https://example.invalid/license", file_sha(upstream))
    receipt = _fetch(source, cache)
    assert receipt["size_bytes"] == 9
    assert _fetch(source, cache) == receipt
    (cache / source.name).write_text("changed", encoding="utf-8")
    with pytest.raises(InputError, match="differs"):
        _fetch(source, cache)


def test_review_validation_aligns_by_token_index(tmp_path):
    cfg = replace(RunConfig.load(CONFIG), data_dir=tmp_path)
    write_rows(cfg.review / "authored-candidates.jsonl", [
        {"message_id": "fixture-a", "family_id": "a", "split": "dev", "text": "Сәлем, завтра!"},
        {"message_id": "fixture-b", "family_id": "b", "split": "test", "text": "Дос, hello!"},
    ])
    path, count = export_review(cfg, "authored", "dev")
    assert count == 1
    with pytest.raises(InputError, match="incomplete"):
        validate_review(cfg, "authored", "dev")
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, dialect="excel-tab")
        rows = list(reader)
        fieldnames = reader.fieldnames
    expected = {"Сәлем": "kk", "завтра": "ru"}
    for row in rows:
        if row["surface"] in expected:
            row["label"] = expected[row["surface"]]
            row["reviewer"] = "fixture"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(reversed(rows))
    gold_path, receipt = validate_review(cfg, "authored", "dev")
    item, = list(read_rows(gold_path))
    assert item["message_label"] == "mixed"
    assert receipt["label_counts"] == {"kk": 1, "ru": 1, "neutral": 2}
    assert item["reviewer_ids"] == ["fixture"]
    assert export_review(cfg, "authored", "dev")[0] == path
    assert validate_review(cfg, "authored", "dev")[1]["gold_sha256"] == receipt["gold_sha256"]


@pytest.mark.parametrize(("labels", "expected"), [
    (["kk", "ru", "ambiguous"], "mixed"),
    (["kk", "neutral"], "non_mixed"),
    (["kk", "ambiguous"], "indeterminate"),
    (["neutral"], "neutral_only"),
])
def test_gold_message_definition(labels, expected):
    assert gold_message_label([{"label": label} for label in labels]) == expected
