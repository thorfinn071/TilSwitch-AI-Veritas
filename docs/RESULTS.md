# TilSwitch AI results

## Locked monolingual evaluation, Nov 14, 2026

Source-internal Tatoeba test with 350 sentences per language, 1,050 sentences in total and 6,673 lexical words. The training split had 2,000 sentences per language and development had 350 per language. Grouped extraction used seed 1729 and protected against known linked translations and near-duplicates. A same-source repeat preparation reproduced all three split hashes.

| Method | Word macro-F1 | Short-message word macro-F1 | Message accuracy | Word coverage |
|---|---:|---:|---:|---:|
| Script and distinctive-letter rule | 0.856 | 0.863 | 0.481 | 0.953 |
| Word-only LR | 0.962 | 0.960 | 0.690 | 0.953 |
| Word and neighbor LR | 0.969 | 0.970 | 0.720 | 0.953 |

A short message has at most five lexical words (521 test messages). Each word inherits its source sentence's language for this test. The three supported word labels have equal weight in macro-F1. An unknown prediction counts against the word's source label. The message metric requires one language across every lexical word. Messages with uncertainty or more than one predicted language fail that strict criterion.

| Method | Kazakh F1 (2,105 words) | Russian F1 (1,936) | English F1 (2,632) |
|---|---:|---:|---:|
| Script rule | 0.794 | 0.797 | 0.975 |
| Word-only LR | 0.979 | 0.930 | 0.975 |
| Word and neighbor LR | 0.990 | 0.941 | 0.975 |

| Method | Kazakh message accuracy | Russian message accuracy | English message accuracy |
|---|---:|---:|---:|
| Script rule | 0.180 | 0.580 | 0.683 |
| Word-only LR | 0.826 | 0.563 | 0.683 |
| Word and neighbor LR | 0.903 | 0.574 | 0.683 |

The word-only model identified **90.5%** of the 717 Kazakh-labeled test words without a distinctive Kazakh letter. The script rule assigned zero of those words to Kazakh and the context model identified **94.6%**. Across all three languages, context added 0.007 word macro-F1 on this dataset. These scores use the base setting with a zero numerical margin threshold. English F1 was 0.975 for all three methods at the displayed precision.

Under the monolingual reference, the script rule flagged 277 of 1,050 messages as mixed (277 Kazakh). The word-only model flagged 72 (58 Kazakh, 14 Russian) and the context model flagged 34 (31 Kazakh, 3 Russian). Each method assigned a supported language to 6,359 of the 6,673 lexical words. [Aggregate evidence](../release/evidence/mono-summary.json)

### Paired error example

| Test input | Reference from source | Script-rule output | Word-only and context outputs |
|---|---|---|---|
| Он адам зардап шекті. | Kazakh for all four words. The initial word is used as the numeral “ten”. | Он адам зардап → Russian. шекті → Kazakh. Mixed evidence. | Он → Russian. адам зардап шекті → Kazakh. Mixed evidence. |

The isolated spelling also occurs as a common Russian pronoun. The outcome illustrates how a word-level error can change the message status. One-character words are an additional source of strict message-level review outcomes. [Tatoeba sentence 2816435, ABChessel](https://tatoeba.org/en/sentences/show/2816435) · [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/)

## Locked KRCS evaluation, Nov 15, 2026

One bilingual reviewer labeled all 12 development and 36 test messages in the screened social-media sample. The test met the planned support gates with 18 short messages, 190 Kazakh words from 36 messages and 62 Russian words from 29 messages. The primary score averages Kazakh and Russian F1 with equal weight. An uncertain prediction counts as an error on those 252 words. The 43 neutral spans and two ambiguous words are outside this word score. This small, Kazakh-heavy sample has seven Kazakh-only messages, zero Russian-only messages and no independently replicated labels. The school-chat example in the app is an authored demonstration. [KRCS paper](https://arxiv.org/html/2503.20007v1#S3.SS2) · [Support gates](ML_RESEARCH_PLAN.md#targets-split-and-deduplication)

### Development selection

The final development sheet had 47 Kazakh and 34 Russian words. The lock tested margin thresholds of 0, 0.10, 0.20 and 0.35. Both learned models selected 0.10, which returns Uncertain when the two highest class scores differ by less than 0.10. The base context model scored 0.80750 macro-F1 and the base word model scored 0.80741. With the selected thresholds, context had 66.0% Kazakh recall and 95.1% coverage. Word-only had 68.1% Kazakh recall and 93.8% coverage. Context missed the Kazakh recall requirement, so the lock selected word-only before test inference. [Frozen lock](../release/evidence/krcs-v1.lock.json)

### Word scores

| Method | Macro-F1 | Kazakh P / R / F1 (190) | Russian P / R / F1 (62) | Coverage |
|---|---:|---:|---:|---:|
| Script rule | 0.541 | 1.000 / 0.395 / 0.566 | 0.351 / 0.984 / 0.517 | 249/252 |
| Word-only, base | 0.890 | 0.988 / 0.889 / 0.936 | 0.756 / 0.952 / 0.843 | 249/252 |
| Word + context, base | 0.886 | 0.966 / 0.911 / 0.938 | 0.786 / 0.887 / 0.833 | 249/252 |
| Word-only, threshold 0.10 (bundled) | **0.897** | 0.988 / 0.884 / 0.933 | 0.787 / 0.952 / 0.861 | 245/252 |
| Word + context, threshold 0.10 | 0.894 | 0.977 / 0.911 / 0.943 | 0.809 / 0.887 / 0.846 | 245/252 |

P and R are precision and recall. The base word model gained 0.348 macro-F1 over the script rule. Context gained 0.344 over the script rule and scored 0.004 below word-only. The 95% paired bootstrap interval for context minus word-only was [−0.041, +0.031], using 2,000 valid resamples of 36 message groups with seed 3701. The word-only threshold improved macro-F1 by 0.008. Errors among assigned words fell from 21/249 to 18/245, and the number of correct words fell from 228 to 227. The aggregate JSON includes the confusion matrices and uncertain outcomes. [Summary](../release/evidence/krcs-summary.json) · [Per-language CSV](../release/evidence/krcs-per-language.csv) · [Bootstrap](../release/evidence/krcs-bootstrap.json)

| Method | Short (70 words) | At switches (76) | Away from switches (176) | Kazakh recall without distinctive letters (115) |
|---|---:|---:|---:|---:|
| Script rule | 0.487 | 0.703 | 0.458 | 0/115 |
| Word-only, base | 0.835 | 0.881 | 0.881 | 94/115 |
| Word + context, base | 0.863 | 0.827 | 0.913 | 99/115 |
| Word-only, threshold 0.10 | 0.850 | 0.887 | 0.891 | 93/115 |
| Word + context, threshold 0.10 | 0.871 | 0.843 | 0.920 | 99/115 |

A short message has at most five lexical words. A word is at a switch when an immediate eligible neighbor in the model's context window has a different reference language. The short slice contains 47 Kazakh and 23 Russian words from 18 messages. The switch slice contains 43 Kazakh and 33 Russian words from 27 messages. The 176 words away from switches come from 33 messages. The slice scores are descriptive. Context scored higher on short messages and away from switches. Word-only scored higher at switches.

### Message flags and examples

| Method | Correct mixed / 29 | Missed mixed | False mixed / 7 | Precision | Recall | F1 | Needs review |
|---|---:|---:|---:|---:|---:|---:|---:|
| Script rule | 19/29 | 10 | 5/7 | 0.792 | 0.655 | 0.717 | 0 |
| Word-only, base | 27/29 | 2 | 6/7 | 0.818 | 0.931 | 0.871 | 1 |
| Word + context, base or threshold 0.10 | 25/29 | 4 | 3/7 | 0.893 | 0.862 | 0.877 | 1 |
| Word-only, threshold 0.10 (bundled) | 26/29 | 3 | 5/7 | 0.839 | 0.897 | 0.867 | 3 |

Needs review counts as a negative mixed prediction. The small non-mixed slice makes the false mixed counts descriptive. The app displays mixed evidence with review wording.

| KRCS test input | Human reference by word | Bundled output by word | Message outcome |
|---|---|---|---|
| 343 · Японский стиль жарасады | RU · RU · KK | RU · RU · KK | Correct mixed flag |
| 385 · Қалаға тек пропускпен кіреді десеші | KK · KK · KK · KK · KK | KK · KK · RU · KK · KK | False mixed flag |
| 127 · лучшая гой | RU · KK | RU · RU | Missed switch |

The Russian root in **пропускпен** may explain the wrong label despite the Kazakh ending. **гой** is the informal spelling of **ғой** in its reference reading. The original excerpts are shown with added human and model labels. [KRCS, Borisov, Kozhirbayev and Malykh](https://github.com/madrugado/KRCS/blob/9f4fea488bd85490c23ba33ebecc9362d901a21e/KRCS.csv) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## CPU timing

On the reference Windows machine with Python 3.11.9, the 0.10-threshold bundle loaded in 32.8 ms after module imports. Across 30 calls each, median/p95 were 0.96/1.86 ms for repeated short inputs and 6.41/8.86 ms for repeated near-limit inputs. These timings cover Python analysis and grouping. Browser, network and interpreter startup time are outside the measurement.

## Reproduce

The packaged model runs offline after installing the pinned core or demo dependencies. Fresh data downloads use the currently available Tatoeba snapshot. Check the published source hashes before comparing exact numbers. The original snapshot used for the benchmark is cached locally and raw source files are excluded from the release. The release includes the [frozen evaluation lock](../release/evidence/mono-v1.lock.json), [aggregate metrics](../release/evidence/mono-summary.json), [per-language scores](../release/evidence/mono-per-language.csv) and [split and source receipts](../release/evidence/data-manifest.json).

~~~powershell
& .\.venv\Scripts\python.exe -m tilswitch fetch
& .\.venv\Scripts\python.exe -m tilswitch prepare
& .\.venv\Scripts\python.exe -m tilswitch train --model word
& .\.venv\Scripts\python.exe -m tilswitch train --model context
& .\.venv\Scripts\python.exe -m tilswitch lock --datasets mono --out artifacts/runs/mono-replay.lock.json
& .\.venv\Scripts\python.exe -m tilswitch evaluate --phase test --lock artifacts/runs/mono-replay.lock.json --out artifacts/runs/mono-replay
& .\.venv\Scripts\python.exe -m tilswitch benchmark
~~~

Use a new run path for each rerun. The monolingual benchmark used train SHA-256 `abf81e3da4780c949eef01d13edd26c2f5d270247645da2960ba79a05280e662` and test SHA-256 `4d751561779616bf8fe5b679f59d11641e77c982770b01903d1e6af41b79495a`. The shipped model is `word-abf81e3da4`. Its inference policy is tied to `krcs-v1.lock.json` by SHA-256 in the bundle metadata. The original word bundle with the zero threshold is available in the [first verified release](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/e725a7e721c4ea156096f0693e94f7fd51c850f6).

Public files support inference, the paired examples and inspection of aggregate scores. An exact KRCS rerun also requires the local reviewed TSVs and a matching training snapshot. [KRCS evaluation lock](../release/evidence/krcs-v1.lock.json) · [Review and replay commands](REVIEW.md)
