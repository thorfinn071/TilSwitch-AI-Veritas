# TilSwitch AI

**Track** AI + Languages · Veritas AI International High School Hackathon 2026

**Contributor** Nurmukhamed Sabit

## The problem

A school group message can switch languages in the middle of a sentence. TilSwitch helps a student find and copy the phrase they need help understanding. Kazakh and Russian share Cyrillic, and a word can combine a Russian root with a Kazakh ending. Informal spelling can also drop the letters that usually distinguish Kazakh.

## What we built

Paste a message into the browser app to highlight likely Kazakh, Russian and English phrases, then use **Copy** beside the phrase you want to ask about. TilSwitch preserves the original wording and marks uncertain words for review. The bundled CPU model runs offline after setup.

~~~powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-demo.lock.txt
& .\.venv\Scripts\python.exe -m experiments.verify_submission
& .\.venv\Scripts\python.exe -m tilswitch demo --bundle release/submission/model
~~~

Run from the repository root. Open the [local demo](http://127.0.0.1:7860), choose **School announcement**, select **Analyze**, and copy **в актовом зале**. The verification command checks the bundled model and aggregate evidence. On macOS or Linux, create the environment with `python3.11 -m venv .venv` and use `.venv/bin/python` for the remaining commands.

## What we added

We extended the Veritas sentence-level language identification starter with per-word labels, original text offsets, and copyable phrases. The app looks up some informal spellings, uses local evidence for one-letter words such as **в**, and flags some borrowings for review.

## How it works

Logistic regression uses TF-IDF features for sequences of one to four characters. It learns from 6,000 Tatoeba sentences, with each word inheriting its sentence's language. We compared it with a script rule and a variant that also sees the closest word on each side. We selected the word-only model on 12 reviewed KRCS development messages because the context variant missed the Kazakh recall requirement.

## Results

**Original KRCS evaluation.** One bilingual reviewer labeled 36 held-out messages with 190 scored Kazakh words and 62 Russian words. The original release assigned a language to 245 of 252 scored words and flagged 5 of 7 Kazakh-only messages as mixed.

| Method | Word macro-F1 | Kazakh F1 | Russian F1 |
|---|---:|---:|---:|
| Script rule | 0.541 | 0.566 | 0.517 |
| Word-only | 0.890 | 0.936 | 0.843 |
| Word + context | 0.886 | 0.938 | 0.833 |
| Original release with uncertainty threshold | **0.897** | 0.933 | 0.861 |

**Later 60-message cutoff comparison.** We compared 0.20 and 0.35 on these KazNLP comments and reviews, then selected 0.35. Codex drafted the labels and one bilingual reviewer confirmed them. Firm alerts fell from **4/26 to 2/26** on resolved single-language references. Both cutoffs detected **20/20** mixed messages, including **10/10** one-word switches. Fourteen references were indeterminate and outside those totals. A lone word now needs a larger gap between its two leading language scores to support a firm alert. We show **Possible switch** for weaker evidence and keep the word highlights. [Aggregate evidence](release/submission/reviewed-switch.json) · [Full results and limits](docs/RESULTS.md)

In **«Қалаға тек пропускпен кіреді десеші»**, all five reference words are Kazakh. The original release labeled **пропускпен** Russian. The submission bundle marks it uncertain and explains the possible Kazakh ending **-пен**. Other borrowings can still be misclassified, and romanized Kazakh can appear as English. Independent confirmation of the new cutoff on school chats is still needed. [KRCS row 385, Borisov, Kozhirbayev and Malykh](https://github.com/madrugado/KRCS/blob/9f4fea488bd85490c23ba33ebecc9362d901a21e/KRCS.csv) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## What we would do next

Ask two bilingual reviewers to label a fresh set of school-style messages independently. Time how quickly students find the phrase they need help with.

## Sources

[Tatoeba](https://tatoeba.org/en/downloads) · [KRCS author release](https://github.com/madrugado/KRCS) · [FLORES-200](https://github.com/facebookresearch/flores) · [KazNLP](https://arxiv.org/abs/2608.00581) · [Veritas project briefs](https://highschoolhackathon.org/briefs) · [scikit-learn](https://scikit-learn.org/stable/) · [Gradio](https://gradio.app/) · [OpenAI Codex](https://openai.com/codex/). See [data, model and credits](docs/DATA_AND_MODELS.md), [results and reproduction](docs/RESULTS.md) and [blind review instructions](docs/REVIEW.md).
