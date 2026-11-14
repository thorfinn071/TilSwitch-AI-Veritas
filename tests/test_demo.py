from html.parser import HTMLParser

from tilswitch.demo import EMPTY, analyze_for_ui, render_result
from tilswitch.infer import analyze


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


def test_missing_model_has_a_clear_error():
    error, markup = analyze_for_ui("Сәлем!", None)
    assert "release bundle" in error
    assert markup == EMPTY
