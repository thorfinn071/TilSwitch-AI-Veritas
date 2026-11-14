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

Logistic regression learns character patterns from 6,000 Tatoeba training sentences. The context variant also sees the closest word on either side. The baseline uses script and distinctive Kazakh letters. I labeled 12 KRCS development messages to choose when to mark a word uncertain and 36 separate messages for testing.

## Results

The **36 held-out KRCS messages** contained 190 Kazakh and 62 Russian scored words. The released word model used an uncertainty threshold chosen on the development set. It labeled 245 of 252 scored words and flagged 5 of the 7 Kazakh-only messages as mixed.

| Method | Word macro-F1 | Kazakh F1 | Russian F1 |
|---|---:|---:|---:|
| Script rule | 0.541 | 0.566 | 0.517 |
| Word-only | 0.890 | 0.936 | 0.843 |
| Word + context | 0.886 | 0.938 | 0.833 |
| Word-only with uncertainty threshold (bundled) | **0.897** | 0.933 | 0.861 |

In **«Қалаға тек пропускпен кіреді десеші»**, the reference labels all five words Kazakh. TilSwitch marked **пропускпен** Russian and flagged the message as mixed. The Russian root takes the Kazakh ending **-пен**. [KRCS row 385, Borisov, Kozhirbayev and Malykh](https://github.com/madrugado/KRCS/blob/9f4fea488bd85490c23ba33ebecc9362d901a21e/KRCS.csv) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

The KRCS test used one bilingual reviewer. On the separate **1,050-sentence Tatoeba benchmark** with sentence-derived labels, the script rule, word model and context model scored **0.856**, **0.962** and **0.969** macro-F1, respectively. [Full results and per-language scores](docs/RESULTS.md)

## What we would do next

Ask a second bilingual reviewer to label a fresh sample with more Kazakh-only messages. Use it to measure how often borrowings and informal spellings cause false mixed flags.

## Sources

[Tatoeba](https://tatoeba.org/en/downloads) · [KRCS author release](https://github.com/madrugado/KRCS) · [Veritas project briefs](https://highschoolhackathon.org/briefs) · [scikit-learn](https://scikit-learn.org/stable/) · [Gradio](https://gradio.app/) · [OpenAI Codex](https://openai.com/codex/). See [data, model and credits](docs/DATA_AND_MODELS.md), [results and reproduction](docs/RESULTS.md) and [blind review instructions](docs/REVIEW.md).
