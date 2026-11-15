# Independent evaluation of the 0.35 release

The holdout contains 40 selected public KazNLP comments and reviews and 16 authored controls. Two reviewers independently labeled the words before seeing predictions. Their lexical labels agreed on 381/383 spans before adjudication, with Cohen’s κ of 0.990. The reviewers jointly resolved the two disagreements and the references were locked before a single paired run. R2's self-reported proficiency level remained unspecified. [KazNLP source and annotation conventions](https://arxiv.org/abs/2608.00581)

## Public messages

| Measure | Frozen 0.35 | Experimental borrowing rule |
| --- | ---: | ---: |
| False firm Mixed on monolingual messages | 3/24 | 3/24 |
| False firm Mixed on Kazakh-only messages | 2/17 | 2/17 |
| False firm Mixed on Russian-only messages | 1/7 | 1/7 |
| Firm Mixed recall | 15/16 | 15/16 |
| One-word switch recall | 10/11 | 10/11 |
| Resolved word coverage | 296/302 | 296/302 |

| Resolved word labels | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Kazakh | 189 | 0.989 | 0.952 | 0.970 |
| Russian | 113 | 0.939 | 0.947 | 0.943 |

The public data are selected examples. The 16 synthetic controls are a separate challenge set. The borrowing candidate downgraded one false firm alert and one correctly detected one-word switch in the controls. The proposal missed the requirement to reduce public false firm alerts, so the submission uses 0.35.

In the controls, all 12 romanized Kazakh words and all 12 unsupported Latin-script words received English highlights. The interface now advises checking those highlights. These controls illustrate a limitation and leave performance on everyday school chats and student speed open.

The locked model manifest SHA-256 was `d628e4fe4778161ab27d4ea424d63061d37ec9bdd0122828d19d1c88dc23a3aa`. The annotation lock SHA-256 was `5613516d9fa5768784297d5b3bd4b7211d2f54801b6266d1b0dc77a949a904ed`. The aggregate results above use the references from that lock.
