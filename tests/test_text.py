import pytest

from tilswitch.infer import analyze
from tilswitch.model import Policy
from tilswitch.text import neighbors, normalize_word, tokenize
from tilswitch.types import InputError


@pytest.mark.parametrize("raw", [
    "Сәлем, завтра сабақ нешеде начинается?",
    "Қалайсың?   завтра\r\n Bring don’t қайта-қайта 🙂 👩🏾‍💻 1️⃣",
    "https://example.org, @test! cабаq 12:30 abc123 😊 \u200d ",
    "ЖІҢІШКЕ ӘҒҚҢӨҰҮҺІ café cafe\u0301",
    "  \n  ",
])
def test_offsets_reconstruct_the_unmodified_message(raw):
    parts = []
    offset = 0
    for token in tokenize(raw):
        assert offset <= token.start < token.end <= len(raw)
        assert raw[token.start:token.end] == token.text
        parts.extend((raw[offset:token.start], token.text))
        offset = token.end
    parts.append(raw[offset:])
    assert "".join(parts).encode("utf-8") == raw.encode("utf-8")


def test_normalization_preserves_kazakh_and_maps_internal_connectors():
    assert normalize_word("ӘҒҚҢӨҰҮҺІ") == "әғқңөұүһі"
    assert normalize_word("I\u0307") == normalize_word("İ")
    assert normalize_word("don’t қайта‑қайта") == "don't қайта-қайта"


def test_masks_and_script_guards():
    raw = "https://example.org, @user #draft 12:30 1️⃣ 👩🏾‍💻 你好 abc123 cабаq I"
    tokens = tokenize(raw)
    by_text = {token.text: token for token in tokens}
    assert by_text["https://example.org"].reason == "link"
    for surface in (",", "@user", "#draft", "12:30", "1️⃣", "👩🏾‍💻"):
        assert by_text[surface].kind == "neutral"
    assert by_text["你好"].reason == "unsupported_or_mixed_script"
    assert by_text["cабаq"].reason == "unsupported_or_mixed_script"
    assert by_text["abc123"].reason == "alphanumeric"
    assert by_text["I"].reason == "short_word"


@pytest.mark.parametrize("raw", ["", " \n ", None, "\ud800", "Сәлем\x00hello", "а" * 1001])
def test_bad_inputs_are_reported(raw):
    with pytest.raises(InputError):
        analyze(raw, None)


def test_status_counts_and_boundaries():
    mixed = analyze("Сәлем, завтра сабақ қайда начинается? I", None, Policy(mixed_review_recommended=False))
    assert mixed["status"] == "mixed"
    assert mixed["counts"] == {"kk": 3, "ru": 2, "en": 0, "unk": 1, "neutral": 2}
    assert mixed["has_unknown"] and mixed["shares"]["kk"] == 0.5
    assert mixed["primary_language"] is None
    assert mixed["segments"][2]["text"] == "сабақ қайда"
    assert analyze("Hello!", None)["primary_language"] == "en"
    assert analyze("Hello I", None)["status"] == "needs_review"
    assert analyze("! 123 🙂", None)["shares"] is None
    assert analyze("!" * 1000, None)["status"] == "neutral_only"


def test_context_stops_at_newline_mask_sentence_break_and_unsupported_word():
    raw = "Сәлем, завтра сабақ? қайта\nорысша 12:30 right cабаq then!"
    tokens = tokenize(raw)
    values = {token.text: pair for token, pair in zip(tokens, neighbors(raw, tokens), strict=True)}
    assert values["завтра"] == ("сәлем", "сабақ")
    assert values["сабақ"][1] == ""
    assert values["қайта"] == ("", "")
    assert values["орысша"] == ("", "")
    assert values["right"] == ("", "")
    assert values["then"] == ("", "")


def test_neutral_and_line_breaks_stop_highlight_merges():
    raw = "hello world,\nhello world"
    result = analyze(raw, None)
    assert [segment["text"] for segment in result["segments"]] == ["hello world", "hello world"]


def test_first_word_on_a_new_line_can_supply_following_context():
    raw = "Сәлем сабақ\r\nқайта келсең хабарла"
    tokens = tokenize(raw)
    assert neighbors(raw, tokens)[2:] == [("", "келсең"), ("қайта", "хабарла"), ("келсең", "")]
