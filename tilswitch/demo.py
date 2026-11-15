from __future__ import annotations

from functools import partial
from html import escape
from pathlib import Path

from .infer import analyze
from .model import Model, load_bundle
from .samples import EXAMPLES
from .types import InputError

CSS_PATH = Path(__file__).with_name("demo.css")
JS_PATH = Path(__file__).with_name("demo.js")
LANGUAGE_NAMES = {"kk": "Kazakh", "ru": "Russian", "en": "English", "unk": "Uncertain"}
REASONS = {
    "short_word": "One-letter word",
    "unsupported_or_mixed_script": "Unsupported or mixed script",
    "alphanumeric": "Letters and digits",
    "unseen_features": "Unfamiliar spelling",
    "script_mismatch": "Language and script disagree",
    "low_margin": "Close model scores",
    "kazakh_ending": "Possible borrowing with a Kazakh ending",
}
EMPTY = (
    '<section class="analysis" aria-label="Language analysis">'
    '<h2>Language analysis</h2><p class="analysis-empty">Your highlighted message will appear here.</p>'
    '</section>'
)


def _literal(text: str) -> str:
    # Keep user braces literal in Gradio's HTML template and escape all markup.
    return escape(text).replace("{", "&#123;").replace("}", "&#125;").replace("\r", "&#13;")


def render_result(result: dict) -> str:
    raw = result["text"]
    highlights = []
    rows = []
    reason_index = {
        token["start"]: REASONS[token["reason"]] for token in result["tokens"]
        if token["label"] == "unk" and token["reason"] in REASONS
    }
    offset = 0
    for number, segment in enumerate(result["segments"], start=1):
        start, end, label = segment["start"], segment["end"], segment["label"]
        content = _literal(raw[start:end])
        highlights.append(_literal(raw[offset:start]))
        attributes = f'class="language-{label}"'
        if label != "unk":
            attributes += f' lang="{label}"'
        highlights.append(f"<mark {attributes}>{content}</mark>")
        reasons = sorted({value for key, value in reason_index.items() if start <= key < end})
        details = f"<small>{' · '.join(reasons)}</small>" if reasons else ""
        rows.append(
            f'<li><span class="language-key language-{label}">{LANGUAGE_NAMES[label]}</span>'
            f'<span class="segment-content" id="phrase-{number}" '
            f'lang="{label if label != "unk" else "und"}">{content}</span>'
            f'<button type="button" class="copy-phrase" aria-label="Copy {LANGUAGE_NAMES[label].lower()} phrase" '
            f'aria-describedby="phrase-{number}">Copy</button>'
            f"{details}</li>"
        )
        offset = end
    highlights.append(_literal(raw[offset:]))
    status = result["status"]
    if status == "mixed":
        title = "Mixed language evidence · review" if result["mixed_review_recommended"] else "Mixed languages"
    elif status == "possible_switch":
        title = "Possible switch"
    elif status == "single" and result["primary_language"] == "en":
        title = "English evidence"
    elif status == "single":
        title = f"{LANGUAGE_NAMES[result['primary_language']]} detected"
    elif status == "needs_review":
        title = "Needs review"
    else:
        title = "No words to analyze"

    counts = []
    for language, name in LANGUAGE_NAMES.items():
        count = result["counts"][language]
        if count:
            counts.append(f'<li class="language-key language-{language}">{name} <strong>{count}</strong></li>')
    legend = f'<ul class="language-counts" aria-label="Word counts">{"".join(counts)}</ul>' if counts else ""
    note = ""
    if status == "possible_switch":
        note = '<p class="analysis-note">The switch depends on a word with close language scores. Check the highlights.</p>'
    if result["has_unknown"]:
        note += '<p class="analysis-note">Review uncertain words before using the result.</p>'
    if result["counts"]["en"]:
        note += (
            '<p class="analysis-note">Check the English highlights if you expect Kazakh typed in Latin letters '
            'or another Latin-script language.</p>'
        )
    groups = (
        '<div class="segment-section"><h3>Detected phrases</h3>'
        f'<ul class="segments">{"".join(rows)}</ul>'
        '<p class="copy-status" role="status"></p></div>' if rows else ""
    )
    return (
        '<section class="analysis" aria-label="Language analysis">'
        '<h2>Language analysis</h2>'
        '<p class="analysis-note stale-result" role="status" hidden>Message changed. Analyze it again to see updated highlights.</p>'
        f'<div class="analysis-content"><p class="analysis-status" role="status">{title}</p>'
        f'<p class="analysis-original" aria-label="Last analyzed message">{"".join(highlights)}</p>'
        f"{legend}{note}{groups}"
        f'<details class="model-details"><summary>About this result</summary>'
        f'<p>Model {escape(result["model_id"])}. Counts include uncertain words and exclude '
        'punctuation, numbers and emojis.</p></details></div></section>'
    )


def analyze_for_ui(raw: str, model: Model | None) -> tuple[str, str]:
    if model is None:
        return "Train a model or point the demo at the included release bundle.", EMPTY
    try:
        return "", render_result(analyze(raw, model))
    except InputError as error:
        return str(error), EMPTY


def _error_markup(message: str) -> str:
    return f'<p role="alert">{_literal(message)}</p>' if message else ""


def _render_request(model: Model | None, raw: str) -> tuple[str, str]:
    error, result = analyze_for_ui(raw, model)
    return _error_markup(error), result


def _reset(value: str, error: str) -> tuple[str, str, str]:
    return value, _error_markup(error), EMPTY


def build_ui(model: Model | None):
    import gradio as gr

    intro = (
        '<header class="tool-intro"><h1>TilSwitch AI</h1>'
        '<p>Find the phrase you need help with in a mixed-language message.</p></header>'
    )
    scope = (
        '<aside class="scope-note"><p>Supports Cyrillic Kazakh, Russian and English. '
        'Short or shared words, names, borrowings and romanized text can be misclassified.</p>'
        '<p>Analysis runs on this device.</p></aside>'
    )
    unavailable = "Train a model or point the demo at the included release bundle." if model is None else ""
    with gr.Blocks(title="TilSwitch AI", analytics_enabled=False) as app:
        with gr.Column(elem_id="workspace"):
            gr.HTML(intro, elem_id="page-intro", js_on_load=None)
            with gr.Row(elem_id="analysis-layout"):
                with gr.Column(elem_id="composer", min_width=0):
                    message = gr.Textbox(
                        "", label="Message", placeholder="Paste a school or group-chat message",
                        lines=3, max_lines=5, info="Up to 1,000 characters", elem_id="source-text",
                    )
                    error = gr.HTML(_error_markup(unavailable), elem_id="input-error", js_on_load=None)
                    with gr.Row(elem_id="actions"):
                        submit = gr.Button("Analyze", variant="primary", scale=0, min_width=118,
                                           interactive=model is not None)
                        clear = gr.Button("Clear", variant="secondary", scale=0, min_width=80)
                    gr.HTML('<div class="example-label">Try an example</div>', js_on_load=None)
                    with gr.Row(elem_id="examples"):
                        examples = [
                            (gr.Button(label, variant="secondary", size="sm", min_width=0), content)
                            for label, content in EXAMPLES
                        ]
                result = gr.HTML(EMPTY, elem_id="analysis-result", min_width=0,
                                 js_on_load=JS_PATH.read_text(encoding="utf-8"))
            gr.HTML(scope, elem_id="app-scope", js_on_load=None)

        request = submit.click(
            partial(_render_request, model), inputs=message, outputs=[error, result],
            show_progress="full", trigger_mode="once", concurrency_limit=1, api_visibility="undocumented",
        )
        for button, example in examples:
            button.click(
                partial(_reset, example, unavailable), outputs=[message, error, result],
                queue=False, cancels=[request], api_visibility="undocumented",
            )
        clear.click(
            partial(_reset, "", unavailable), outputs=[message, error, result], queue=False,
            cancels=[request], api_visibility="undocumented",
        )
    return app


def launch(bundle: Path, port: int) -> None:
    try:
        model = load_bundle(bundle)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f"TilSwitch: {error}")
        model = None
    app = build_ui(model)
    app.launch(server_name="127.0.0.1", server_port=port, share=False, run_history=False, inbrowser=False,
               footer_links=[], mcp_server=False, enable_monitoring=False,
               css=CSS_PATH.read_text(encoding="utf-8"))
