from html.parser import HTMLParser
from types import SimpleNamespace

from tilswitch.demo import EMPTY, analyze_for_ui, render_result
from tilswitch.infer import analyze
from tilswitch.model import Policy
from tilswitch.word_evidence import WordEvidence


class OriginalText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "p" and ("class", "analysis-original") in attrs:
            self.active = True

    def handle_endtag(self, tag):
        if tag == "p":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def test_result_reconstructs_raw_text_and_escapes_markup():
    raw = "Қалайсың?  завтра\r\n Bring <note> & {{draft}} 🙂"
    markup = render_result(analyze(raw, None))
    parser = OriginalText()
    parser.feed(markup)
    assert "".join(parser.parts) == raw
    assert "note" not in parser.tags
    assert "{{draft}}" not in markup
    assert "Mixed language evidence" in markup
    assert "Detected phrases" in markup


def test_render_shows_uncertainty_as_readable_text():
    markup = render_result(analyze("你好 👋 12:30", None))
    assert "Needs review" in markup
    assert "Unsupported or mixed script" in markup
    assert "Uncertain" in markup


def test_result_shows_latin_script_caution_for_english_highlights():
    guidance = "Check the English highlights if you expect Kazakh typed in Latin letters or another Latin-script language."
    english = render_result(analyze("Bring the folder", None))
    assert "English evidence" in english and guidance in english
    assert 'lang="en">Bring the folder</mark>' in english
    mixed = render_result(analyze("Кел ertenge", None))
    assert "Mixed language evidence" in mixed and guidance in mixed
    assert guidance not in render_result(analyze("Ертең мектепке кел", None))


def test_possible_switch_keeps_the_one_word_highlight():
    raw = "Сәлем, завтра барамыз"
    model = SimpleNamespace(model_id="fixture", mode="word", classes=("kk", "ru", "en"), policy=Policy(0.10),
                            probabilities=lambda rows: ([(.90, .08, .02), (.35, .60, .05), (.90, .08, .02)], [1, 1, 1]))
    mixed = analyze(raw, model)
    possible = analyze(raw, model, Policy(0.10, singleton_switch_margin=0.35))
    assert mixed["status"] == "mixed"
    assert possible["status"] == "possible_switch"
    assert possible["primary_language"] is None
    assert possible["tokens"] == mixed["tokens"]
    assert possible["segments"] == mixed["segments"]
    markup = render_result(possible)
    assert "Possible switch" in markup
    assert 'lang="ru">завтра</mark>' in markup
    assert analyze(raw, model, Policy(0.10, singleton_switch_margin=0.20))["status"] == "mixed"


def test_borrowing_review_requires_a_plausible_stem_and_local_kazakh_context():
    scores = {
        "проектормен": (.27, .71, .02),
        "проекторпен": (.27, .71, .02),
        "проектор": (.07, .92, .01),
        "жұмыс": (.95, .04, .01),
        "істейміз": (.99, .01, .0),
        "позже": (.02, .97, .01),
    }

    def probabilities(rows):
        return [scores[row.surface] for row in rows], [1] * len(rows)

    model = SimpleNamespace(model_id="fixture", mode="word", classes=("kk", "ru", "en"),
                            policy=Policy(0.10, review_kazakh_borrowings=True), probabilities=probabilities)
    raw = "Проектормен жұмыс істейміз"
    assert analyze(raw, model, Policy(0.10))["status"] == "mixed"
    reviewed = analyze(raw, model)
    assert reviewed["status"] == "needs_review"
    assert reviewed["tokens"][0] == {"text": "Проектормен", "start": 0, "end": 11,
                                     "label": "unk", "reason": "kazakh_ending"}
    assert "Possible borrowing with a Kazakh ending" in render_result(reviewed)
    assert analyze("Проектормен. Жұмыс істейміз", model)["status"] == "mixed"
    assert analyze("Проекторпен жұмыс істейміз", model)["status"] == "mixed"
    assert analyze("Жұмыс позже істейміз", model)["status"] == "mixed"


def test_short_words_join_supported_phrases_and_leave_isolated_letters_uncertain():
    labels = {"ертең": "kk", "актовом": "ru", "зале": "ru", "room": "en"}
    languages = ("kk", "ru", "en")

    def probabilities(rows):
        return [tuple(.98 if lang == labels[row.surface] else .01 for lang in languages)
                for row in rows], [1] * len(rows)

    model = SimpleNamespace(model_id="fixture", mode="word", classes=languages, policy=Policy(0.10),
                            word_evidence=WordEvidence(frozenset(), frozenset()), probabilities=probabilities)
    result = analyze("Ертең в актовом зале", model)
    assert result["segments"][1] == {"label": "ru", "text": "в актовом зале", "start": 6, "end": 20}
    assert analyze("Ертең в. Актовом зале", model)["tokens"][1]["label"] == "unk"
    assert analyze("в", model)["tokens"][0]["label"] == "unk"
    assert analyze("Room A", model)["tokens"][1]["label"] == "unk"


def test_spelling_recovery_uses_local_kazakh_or_parallel_word_evidence():
    labels = {"күн": "kk", "далага": "ru", "лучшая": "ru", "гой": "ru"}
    languages = ("kk", "ru", "en")

    def probabilities(rows):
        return [tuple(.98 if lang == labels[row.surface] else .01 for lang in languages)
                for row in rows], [1] * len(rows)

    evidence = WordEvidence(frozenset({"далага", "гой"}), frozenset({"гой"}))
    model = SimpleNamespace(model_id="fixture", mode="word", classes=languages, policy=Policy(0.10),
                            word_evidence=evidence, probabilities=probabilities)
    local = analyze("Күн далага", model)
    assert local["primary_language"] == "kk"
    assert local["segments"][0]["text"] == "Күн далага"
    assert analyze("Күн. далага", model)["tokens"][-1]["label"] == "ru"
    assert [token["label"] for token in analyze("Лучшая гой", model)["tokens"]] == ["ru", "kk"]


def test_missing_model_has_a_clear_error():
    error, markup = analyze_for_ui("Сәлем!", None)
    assert "release bundle" in error
    assert markup == EMPTY
