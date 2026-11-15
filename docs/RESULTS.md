# TilSwitch AI results

The contest package loads the verified 0.35 bundle in `release/submission/model`. See the [84-message development comparison](COMPETITION_DEVELOPMENT.md) and the [56-message diagnostic with corrected annotation provenance](INDEPENDENT_RESULTS.md). The chronological results below document earlier training, evaluation and cutoff selection.

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
| Original release, threshold 0.10 | **0.897** | 0.988 / 0.884 / 0.933 | 0.787 / 0.952 / 0.861 | 245/252 |
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
| Original release, threshold 0.10 | 26/29 | 3 | 5/7 | 0.839 | 0.897 | 0.867 | 3 |

Needs review counts as a negative mixed prediction. The small non-mixed slice makes the false mixed counts descriptive. The app displays mixed evidence with review wording.

| KRCS test input | Human reference by word | Original release output by word | Message outcome |
|---|---|---|---|
| 343 · Японский стиль жарасады | RU · RU · KK | RU · RU · KK | Correct mixed flag |
| 385 · Қалаға тек пропускпен кіреді десеші | KK · KK · KK · KK · KK | KK · KK · RU · KK · KK | False mixed flag |
| 127 · лучшая гой | RU · KK | RU · RU | Missed switch |

The Russian root in **пропускпен** may explain the wrong label despite the Kazakh ending. **гой** is the informal spelling of **ғой** in its reference reading. The original excerpts are shown with added human and model labels. [KRCS, Borisov, Kozhirbayev and Malykh](https://github.com/madrugado/KRCS/blob/9f4fea488bd85490c23ba33ebecc9362d901a21e/KRCS.csv) · [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Updated switch and borrowing policy, Nov 15, 2026

The new policy uses the original trained word model. It returns **Possible switch** when there is too little evidence to make a firm mixed call. A single word can support a firm switch when its top two class scores differ by at least 0.20. Two accepted words in the same language also count as evidence. The borrowing check asks for review when an instrumental ending fits a Russian-looking stem, removing the ending strengthens the stem's Russian score, and a nearby word supplies Kazakh evidence. In KRCS row 385 the app now marks **пропускпен** uncertain and explains the possible Kazakh ending.

Development compared several one-word margins on the author-provided KazNLP validation split (462 messages), the 12 reviewed KRCS development messages and 12 scripted school cases. The 0.20 margin reduced firm mixed calls on single-language references from 107 to 99 on KazNLP validation, with 160 of 162 clause-level mixed messages detected in both runs. It retained each mixed and one-word detection count on the two smaller development sets. The policy was fixed before scoring the published KazNLP test split. The exact and near-duplicate screen checked the training, KRCS and scripted inventories as well as the upstream validation/test boundary. All 461 author test messages passed screening. [Author splits](https://github.com/naadgob/KazNLP/tree/f5d5be8108179aded06e145ad6eb019489f207e4/data/training/filter/v1) · [Annotation paper](https://arxiv.org/abs/2608.00581)

| KazNLP test outcome | Original release | Updated policy |
|---|---:|---:|
| Firm mixed on Kazakh-only reference | 49/150 | 47/150 |
| Firm mixed on Russian-only reference | 38/150 | 35/150 |
| Firm mixed on clause-level mixed reference | 159/161 | 159/161 |
| Possible switch on a single-language reference | 0/300 | 5/300 |

KazNLP uses document labels and counts clause-level alternation. This benchmark measures how often the app makes a firm mixed call against those labels. The five changes moved to **Possible switch**, with the word highlights still visible.

On the previously scored 36-message KRCS replay, firm false mixed flags fell from 5 to 4 of 7, true mixed detection stayed at 26 of 29, and genuine one-word switch detection stayed at 15 of 17. Word macro-F1 was 0.897 and 0.904 respectively, while coverage decreased from 245 to 243 of 252 scored words. On the 20 AI-authored challenge messages, firm false mixed flags fell from 4 to 2 of 12, with all eight scripted mixed messages detected in both runs. Informal spellings remain a source of missed switches. These counts do not measure usability in live school chats. [Aggregate evidence](../release/evidence/borrowing-review.json)

For a local reproduction, download the pinned author files `val.csv` and `test.csv` into one folder. Use the original prepared Tatoeba training split and validated KRCS sheets. Place the [original bundle](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/988119e483ffd6b8c26e9543a98e7ec044e592d0/release/model) in `artifacts/models/krcs-release`, or point `--baseline` to that bundle. Run `python -m experiments.borrowing_review --kaznlp-dir PATH_TO_FOLDER`.

## Informal spellings and short words, Nov 15, 2026

The word-recovery bundle in `release/model` uses the original trained weights and adds two sources of word evidence. It may recognize a Kazakh spelling with distinctive letters omitted when a confident Kazakh word is nearby. A smaller set has independent support from at least two non-overlapping KRCS original–translation groups and can be recognized without a Kazakh neighbor. The lookup excludes spellings also observed in the original Russian training words or in a Russian translation used to build the lookup. The 48 reviewed KRCS groups and near-duplicates of their variants were excluded from building it. Alignments supply weak evidence. The two language references sometimes share or paraphrase a word.

A common one-letter word can join an adjacent phrase with enough language evidence. Context stops at sentence punctuation, line breaks, numbers, links and unsupported words. The app preserves the original spelling and offsets. It can now copy **в актовом зале** as one Russian phrase and recognize the authored **Кун ашык далага шыгамыз** as Kazakh.

We selected the evidence rules on the existing development sets and 100 paired FLORES `dev` groups, then froze the code, model and test inventory. The FLORES `devtest` benchmark uses 200 disjoint groups. Each group contributes six controlled examples. The plain samples inherit their source language. The informal version removes distinctive Kazakh letters, and each mixed variant inserts one word whose source language is known. The source screening checks against the original training text, all accessible KRCS variants and the upstream development groups. These are constructed examples from human translations. [FLORES-200 source](https://github.com/facebookresearch/flores)

| Frozen check | Prior review policy | With word recovery |
|---|---:|---:|
| Correct Kazakh words after distinctive letters were removed | 841/1,200 | 941/1,200 |
| Firm mixed calls on those Kazakh fragments | 162/200 | 124/200 |
| Correct Russian words in plain fragments | 1,033/1,200 | 1,132/1,200 |
| Correct English words in plain fragments | 1,165/1,200 | 1,192/1,200 |
| Correct inserted Russian word | 189/200 | 189/200 |
| Correct inserted Kazakh word | 194/200 | 194/200 |
| KRCS replay word macro-F1 | 0.904 | 0.922 |
| KRCS replay word coverage | 243/252 | 244/252 |
| KRCS replay genuine one-word switches detected | 15/17 | 16/17 |

On the 36-message replay, total mixed detection rose from 26 to 27 of 29. Four of seven Kazakh-only messages still produced a firm mixed flag. On the KazNLP replay, the counts stayed at 47 of 150 for Kazakh-only references, 35 of 150 for Russian-only references and 159 of 161 for clause-level mixed references. The latest bundle still treats some integrated loans as Russian. KRCS row 36 remains a false flag on the attached form **Платныйма**. These measurements support targeted accuracy improvements. Live school-chat coverage still needs a fresh bilingual-reviewed test. [Aggregate evidence](../release/evidence/word-recovery.json)

To rebuild the evidence with the frozen local data, use the same original bundle and author files as the borrowing-policy check. Place the pinned FLORES archive in `data/raw`. Run `python -m experiments.word_recovery lock --out artifacts/runs/word-recovery-recheck --kaznlp-dir PATH_TO_FOLDER`, then run the same command with `score` in place of `lock`.

## Firm Mixed alert cutoff selection, Nov 15, 2026

The locked comparison used the word-recovery bundle and two cutoffs for a single word to support a firm Mixed alert. The candidate raises that cutoff from 0.20 to 0.35. Both policies use a 0.10 word-label threshold and produce identical word labels, highlights and coverage. The decision rule required fewer false firm alerts and at least the same number of detected mixed messages and one-word switches.

The held-out batch contains 60 short, deliberately selected public comments and reviews from the upstream KazNLP training split. Codex drafted the word labels and one bilingual reviewer confirmed them with the prefilled labels visible. Independent reviewer agreement is unmeasured. Fourteen messages have an indeterminate reference and are excluded from the binary alert scores. [Pinned KazNLP source](https://github.com/naadgob/KazNLP/blob/f5d5be8108179aded06e145ad6eb019489f207e4/data/training/filter/v1/train.csv)

| Cutoff-selection outcome | 0.20 cutoff | 0.35 candidate |
|---|---:|---:|
| Firm Mixed on resolved single-language references | 4/26 | 2/26 |
| Firm Mixed on Kazakh-only references | 0/6 | 0/6 |
| Firm Mixed on Russian-only references | 4/20 | 2/20 |
| Firm Mixed on confirmed mixed references | 20/20 | 20/20 |
| Firm Mixed on confirmed one-word switches | 10/10 | 10/10 |
| Firm Mixed on indeterminate references | 11/14 | 10/14 |

The candidate moved two Russian-only messages and one indeterminate message to Possible switch. Both policies assigned a language to 507 of 509 scored Kazakh and Russian words. Kazakh recall was 225/228 and Russian recall was 274/281. We chose 0.35 using this comparison and its locked decision rule. The cutoff still needs independent confirmation. The six resolved Kazakh-only messages and ten one-word switches give limited information about error rates on other texts. [Submission bundle and aggregate evidence](../release/submission/reviewed-switch.json)

Run `python -m experiments.verify_submission` in the contest checkout to check the release bundle against the aggregate evidence. An exact historical replay uses the [packaging command](../experiments/package_reviewed_switch.py) from local commit `750660a`, with the original lock, local reviewed annotations and matching Windows environment. The historical lock binds code as well as data. The command checks the locked decision rule and writes a new candidate directory.

```powershell
python -m experiments.package_reviewed_switch --lock artifacts/runs/reviewed-switch-v1/lock.json --out artifacts/reviewed-switch-replay
python -m tilswitch demo --bundle release/submission/model
```

Use a new `--out` path for another run. Reproduce the comparison with the fixed 0.20 reference in `release/model`. Keep the raw annotations local.

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
