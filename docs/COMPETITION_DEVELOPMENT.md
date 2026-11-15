# Contest release development checks

The contest app loads the fixed 0.35 bundle. We compared alert and context variants on 84 development cases and checked changes to Copy and uncertainty display in Chrome. The underlined words and punctuation-aware spans use the same word labels and Mixed decisions as the frozen model.

## Development comparison

The cohorts were 60 development comments with Codex-drafted labels confirmed by R1, 12 KRCS development messages labeled by one bilingual reviewer, and 12 authored development cases. Across the three cohorts there are 16 resolved Kazakh-only, 23 Russian-only, 36 mixed and nine indeterminate messages. The phrase column counts exact matches of the label and both endpoints against maximal reference spans. Internal soft punctuation may join same-language words.

| Variant | False firm Mixed KK | False firm Mixed RU | Firm Mixed detected | One-word detected | Possible switch | Word coverage | Exact spans recovered |
|---|---:|---:|---:|---:|---:|---:|---:|
| Script and letter rule | 14/16 | 0/23 | 30/36 | 13/17 | 0/84 | 600/622 | 53/177 |
| Saved 0.20 | 6/16 | 4/23 | 36/36 | 17/17 | 1/84 | 604/622 | 129/177 |
| Saved 0.35 | 6/16 | 2/23 | 36/36 | 17/17 | 3/84 | 604/622 | 129/177 |
| Context on every eligible word | 4/16 | 0/23 | 29/36 | 11/17 | 7/84 | 589/622 | 110/177 |
| Shared-word alert downgrade | 6/16 | 2/23 | 36/36 | 17/17 | 3/84 | 604/622 | 129/177 |
| Shared-word reclassification with context | 6/16 | 2/23 | 36/36 | 17/17 | 3/84 | 604/622 | 129/177 |

The selective alternatives check a single outlier word that appears at least twice in each weak training vocabulary and has two neighbors labeled in the other language. One alternative lowers the alert and keeps the word label. The other relabels the word only if the contextual model agrees with the neighbors. The first can downgrade the error on `Он адам зардап шекті.` and also treats an intended Russian pronoun in `Он кеше келді.` as tentative. Neither improves the reviewed development metrics. The all-context variant loses seven baseline firm detections. [Aggregate counts](../release/evidence/context-dev.json) · [Development evaluator](../experiments/context_review.py)

Among the 0.35 false firm alerts on the reviewed development cohorts, four of the six Kazakh-only errors involved borrowings with Kazakh inflection. The other two involved a brand and an anonymized name. Two Russian-only alerts came from Russian forms the model highlighted as Kazakh. The original instrumental-ending check sends some borrowings such as `пропускпен` to review. The separate dative/accusative candidate lowered two false alerts on development, changed zero public outcomes in the 56-message diagnostic and downgraded one genuine switch in a control. [Diagnostic and annotation provenance](INDEPENDENT_RESULTS.md)

The short-word rule correctly joins `в` to `актовом зале`, and the spelling rules recover `Кун ашык далага шыгамыз` in a smoke case. The app still guesses English for `Salem qalaysyn`. An experimental English vocabulary check withheld some valid short-English highlights in its separate stress test. The contest app keeps the prior English predictions and displays a scope note when it highlights Latin text as English.

## Reproduce

From the contest checkout with the [pinned environment](../README.md#what-we-built), point the dev evaluator to the original workspace containing the frozen development labels, Tatoeba training split and trained context bundle.

~~~powershell
python -m experiments.context_review --original ../veritas --out artifacts/context-dev-replay.json
python -m experiments.verify_submission
python -m pytest -q
python -m tilswitch demo --bundle release/submission/model
~~~

For a same-build contrast, launch with `--bundle release/model` to use 0.20. This is a different message cutoff on the same word assets. The 56-message score has its own historical lock and covers the two policies in that lock.

## Browser checks

| Input | 0.35 before the interface changes | Contest build |
|---|---|---|
| `Ертең в актовом зале жиналамыз.` | Copy returned `в актовом зале` | Same clipboard result |
| `Ертең в актовом зале,  сразу после уроков жиналамыз.` | Two Russian segments and two Copy buttons | One Russian segment. Clipboard contains the comma and both spaces |
| `Бүгін ссылка дайын` | Possible switch with ordinary Russian highlighting | Possible switch with the word `ссылка` underlined and described as tentative |
| `Асханаға позже барамыз` | Firm Mixed with `позже` labeled Russian | Same result |
| `Он адам зардап шекті.` | False firm Mixed caused by the label on `Он` | Same reproducible failure |

In Chrome, `пропускпен` was marked Uncertain with a reason. `Salem qalaysyn` received English evidence with a scope note. A separate paired dev pass checked that grouping and display changes preserve word and alert metrics.

Before and after the interface changes, all token labels, reasons, and message statuses matched on **1,134 development inputs** (84 reviewed or authored inputs and 1,050 Tatoeba dev inputs). Against the same 177 annotated span boundaries, exact phrase matches rose from **106 to 129**. This measures the spans offered for copy on development, with the new grouping definition applied once to the references. It does not measure student performance.
