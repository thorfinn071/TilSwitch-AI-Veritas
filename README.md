# TilSwitch AI

**Track** AI + Languages · Veritas AI International High School Hackathon 2026

**Team** Solo entrant · details in the official submission

## The problem

A school announcement can start in Kazakh and switch to Russian for the meeting place. A student who follows the Kazakh can still miss where to go. TilSwitch highlights the phrase they need to ask about or translate.

## What we built

Paste `Ертең в актовом зале,  сразу после уроков жиналамыз.` and select **Analyze**. TilSwitch marks `Ертең` and `жиналамыз` as Kazakh and offers **Copy** for `в актовом зале,  сразу после уроков`, preserving the comma and both spaces. A dotted underline flags a **Possible switch** when the evidence is weaker. After setup, analysis runs offline on your CPU.

Run from the repository root with Python 3.11, then open the [local demo](http://127.0.0.1:7860).

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-demo.lock.txt
& .\.venv\Scripts\python.exe -m experiments.verify_submission
& .\.venv\Scripts\python.exe -m tilswitch demo --bundle release/submission/model
```

On macOS or Linux, use `python3.11` for setup and `.venv/bin/python` for the last three commands.

## What we added

The Veritas starter predicts one language for a sentence. TilSwitch finds where languages change, groups adjacent words into copyable phrases, and asks for review when a single word gives weak evidence of a switch. [Language identification starter](https://highschoolhackathon.org/briefs)

## How it works

Logistic regression learns character patterns from 6,000 Tatoeba sentences, 2,000 per language. Words inherit the sentence label. We grouped linked translations and screened near-duplicates before splitting. The contest build uses a **0.10** word-score margin and spelling evidence. A lone word needs a gap of **0.35** between its top two scores to trigger **Mixed**. [Data and model card](docs/DATA_AND_MODELS.md)

## Results

| Evaluation | Kazakh word F1 | Russian word F1 | Message-level results |
| --- | ---: | ---: | --- |
| KRCS script-rule baseline · 36 test messages | 0.566 | 0.517 | 19/29 mixed detected |
| KRCS original learned model · same 36 messages | **0.933** | **0.861** | 26/29 mixed detected, 5/7 Kazakh-only falsely flagged |
| Contest build 0.35 · 40 selected public KazNLP messages | **0.970** | **0.943** | 15/16 firm Mixed, including 10/11 one-word switches. False alarms on 2/17 Kazakh-only and 1/7 Russian-only messages. |

On the same KRCS test, word macro-F1 rose from **0.541** to **0.897**. In the earlier monolingual Tatoeba benchmark, English word F1 was **0.975** for both the script rule and the word-only model. The contest build’s 56-message diagnostic included 16 authored controls alongside the public texts. Two human reviewers independently reproduced the AI-assisted scoring references after the run. [Full results](docs/RESULTS.md) · [Review audit](docs/INDEPENDENT_RESULTS.md)

**Where it fails.** In `Он адам зардап шекті.` the reference is entirely Kazakh. The contest build labels `Он` as Russian and reports **Mixed**. Here it means “ten” in Kazakh and shares its spelling with the Russian word for “he”. Romanized Kazakh such as `Salem qalaysyn` can also be labeled English. [Attributed test example](docs/RESULTS.md#paired-error-example)

## What we’d do next

Measure how quickly and accurately students find the right phrase, with and without highlights. Test short switches and shared spellings on fresh, bilingual-reviewed messages. [Student pilot plan](docs/PHRASE_FINDING_PILOT.md)

## Sources

[Datasets, licenses, prior work and tools](docs/DATA_AND_MODELS.md) · [Contest bundle and evidence check](experiments/verify_submission.py)
