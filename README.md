# TilSwitch AI

**Track** AI + Languages · Veritas AI International High School Hackathon 2026

**Contributor** Nurmukhamed Sabit

## The problem

A school group message can move between Kazakh and Russian within a sentence. TilSwitch helps a student find the phrase they want to ask about or translate.

## What we built

Paste a message into the browser app to highlight likely Kazakh, Russian and English phrases. TilSwitch preserves the original wording and marks uncertain words for review. The bundled CPU model runs offline after setup.

~~~powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-demo.lock.txt
& .\.venv\Scripts\python.exe -m tilswitch demo
~~~

Open the [local demo](http://127.0.0.1:7860) after launching it from the repository root. With Python 3.11 on macOS or Linux, use `python3.11 -m venv .venv` and `.venv/bin/python` for the remaining commands. The CLI also works with `requirements-core.lock.txt` in place of the demo lock. Run `python -m tilswitch analyze --text "Сәлем, завтра сабақ нешеде начинается?"` using that environment's Python.

## What we added

The Veritas language identification starter assigns one label per sentence. We built a per-word classifier and phrase highlighter, then tested whether nearby words help distinguish two languages that share Cyrillic.

## How it works

Logistic regression learns character patterns from 6,000 Tatoeba training sentences. The context variant also sees the closest word on either side. Both use the same input checks as the baseline, which uses script and distinctive Kazakh letters.

## Results

On **1,050 held-out Tatoeba sentences**, each word inherits its source sentence's language. All three methods assigned a language to 6,359 of 6,673 words. The separate KRCS mixed-message benchmark is awaiting bilingual reference labels.

| Method | Word macro-F1 | Kazakh F1 | Russian F1 | English F1 |
|---|---:|---:|---:|---:|
| Script rule | 0.856 | 0.794 | 0.797 | 0.975 |
| Word-only (bundled) | **0.962** | 0.979 | 0.930 | 0.975 |
| Word + context | 0.969 | 0.990 | 0.941 | 0.975 |

Tatoeba labels **«Он адам зардап шекті.»** Kazakh. TilSwitch marked **Он** Russian and **адам зардап шекті** Kazakh, triggering a mixed flag. **Он** also forms a common Russian pronoun. [Tatoeba sentence 2816435, ABChessel](https://tatoeba.org/en/sentences/show/2816435) · [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/)

## What we would do next

Complete blind bilingual review and measure whether context helps at real switch boundaries without reducing Kazakh recall or coverage.

## Sources

[Tatoeba](https://tatoeba.org/en/downloads) · [KRCS author release](https://github.com/madrugado/KRCS) · [Veritas project briefs](https://highschoolhackathon.org/briefs) · [scikit-learn](https://scikit-learn.org/stable/) · [Gradio](https://gradio.app/) · [OpenAI Codex](https://openai.com/codex/). See [data, model and credits](docs/DATA_AND_MODELS.md), [results and reproduction](docs/RESULTS.md) and [blind review instructions](docs/REVIEW.md).
