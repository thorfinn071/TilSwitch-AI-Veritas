# TilSwitch AI results

## Locked monolingual evaluation, Nov 14, 2026

Source-internal Tatoeba test with 350 sentences per language, 1,050 sentences in total and 6,673 lexical words. The training split had 2,000 sentences per language and development had 350 per language. Grouped extraction used seed 1729 and protected against known linked translations and near-duplicates. A same-source repeat preparation reproduced all three split hashes.

| Method | Word macro-F1 | Short-message word macro-F1 | Message accuracy | Word coverage |
|---|---:|---:|---:|---:|
| Script and distinctive-letter rule | 0.856 | 0.863 | 0.481 | 0.953 |
| Word-only LR, included in release | 0.962 | 0.960 | 0.690 | 0.953 |
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

The word-only model identified **90.5%** of the 717 Kazakh-labeled test words without a distinctive Kazakh letter. The script rule assigned zero of those words to Kazakh and the context model identified **94.6%**. Across all three languages, context added 0.007 word macro-F1 on this dataset. Its selection gate requires independent bilingual development labels, so the included release uses the word-only model. English gains over the script rule were absent at the displayed precision.

Under the monolingual reference, the script rule flagged 277 of 1,050 messages as mixed (277 Kazakh). The word-only model flagged 72 (58 Kazakh, 14 Russian) and the context model flagged 34 (31 Kazakh, 3 Russian). Each method assigned a supported language to 6,359 of the 6,673 lexical words. [Aggregate evidence](../release/evidence/mono-summary.json)

### Paired error example

| Test input | Reference from source | Script-rule output | Word-only and context outputs |
|---|---|---|---|
| Он адам зардап шекті. | Kazakh for all four words. The initial word is used as the numeral “ten”. | Он адам зардап → Russian. шекті → Kazakh. Mixed evidence. | Он → Russian. адам зардап шекті → Kazakh. Mixed evidence. |

The isolated spelling also occurs as a common Russian pronoun. The outcome illustrates how a word-level error can change the message status. One-character words are an additional source of strict message-level review outcomes. [Tatoeba sentence 2816435, ABChessel](https://tatoeba.org/en/sentences/show/2816435) · [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/)

## KRCS external evaluation pending human review

At the Nov 14 review check, all 83 development and 260 held-out lexical rows still required human labels and reviewer codes. The 12 development and 36 held-out messages remain available for blind review. The release uses the word-only model with a zero numerical margin threshold and the existing script and input checks. KRCS scores, support by reference language and reviewer agreement are pending. The app's school-chat example is an authored demonstration of the workflow. [Review procedure](REVIEW.md) · [Support gates](ML_RESEARCH_PLAN.md#targets-split-and-deduplication)

## CPU timing

On the reference Windows machine with Python 3.11.9, the included model bundle loaded in 21.7 ms after module imports. Across 30 calls each, median/p95 were 0.65/0.74 ms for repeated short inputs and 3.92/4.42 ms for repeated near-limit inputs. These times cover Python analysis and grouping. Browser, network and interpreter startup time are outside the measurement.

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

Use a new run path for each rerun. The original run used train SHA-256 `abf81e3da4780c949eef01d13edd26c2f5d270247645da2960ba79a05280e662` and test SHA-256 `4d751561779616bf8fe5b679f59d11641e77c982770b01903d1e6af41b79495a`. The shipped model identifier is `word-abf81e3da4`. [Review procedure](REVIEW.md)
