# TilSwitch AI

**Track** AI + Languages · Veritas AI International High School Hackathon 2026

**Contributor** Nurmukhamed Sabit

## The problem

A school group message can switch languages mid-sentence. A student may understand the announcement but miss where to meet. TilSwitch helps them find the phrase to ask about or translate.

## What we built

Paste **Ертең в актовом зале жиналамыз.** and copy **в актовом зале**. TilSwitch highlights likely Kazakh, Russian and English spans. **Possible switch** underlines words with weaker evidence. Copy retains punctuation and spacing inside the span. The CPU model runs offline after setup.

~~~powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-demo.lock.txt
& .\.venv\Scripts\python.exe -m experiments.verify_submission
& .\.venv\Scripts\python.exe -m tilswitch demo --bundle release/submission/model
~~~

Run from the repository root and open the [local app](http://127.0.0.1:7860). On macOS or Linux use `python3.11` to create the environment and `.venv/bin/python` to run the commands.

## What we added

We extended the Veritas sentence-level starter to locate word-level switch boundaries and give each language span its own Copy action. Local rules handle some informal spellings, short words and borrowings.

## How it works

Logistic regression learns character patterns from 6,000 Tatoeba sentences. Each training word inherits its sentence label. We selected the word-only model after comparing a context variant on reviewed development messages. The submission uses a 0.10 word-label margin and a 0.35 firm-alert margin for a lone word.

## Results

| Evaluation | Result |
|---|---|
| Original KRCS test, 36 messages with one bilingual reviewer | Word macro-F1 **0.541** for the script rule and **0.897** for the original release. F1 **0.933 KK**, **0.861 RU**. Coverage **245/252**. False Mixed on **5/7** Kazakh-only messages. |
| Submission model 0.35, 40 public messages from a frozen 56-message diagnostic | **15/16** firm Mixed detections and **10/11** one-word switches. False Mixed on **2/17 KK** and **1/7 RU**. Word F1 **0.970 KK**, **0.943 RU**. Coverage **296/302**. |

The 56-message references used one returned worksheet and a second pass by ChatGPT. Independent human validation is pending. [Annotation audit](docs/INDEPENDENT_RESULTS.md) · [Results and reproduction](docs/RESULTS.md)

**Known failure.** In **Он адам зардап шекті.**, the Kazakh numeral meaning “ten” receives a Russian label and triggers Mixed. Romanized Kazakh can also receive English highlights. [Attributed example and expected labels](docs/RESULTS.md#paired-error-example)

## Next steps

Collect two verified human reviews on fresh school-style messages and [measure phrase-finding time and accuracy with students](docs/PHRASE_FINDING_PILOT.md).

## Sources

[Data, prior work and tool credits](docs/DATA_AND_MODELS.md)
