# Locked 56-message evaluation and human reference check

The batch contains 40 selected public KazNLP comments and reviews and 16 authored controls. The entrant confirmed that human reviewers R1 and R2 independently filled blank copies without seeing the other labels or model predictions. No AI assistance was reported for either human review. They agreed on **383/383** lexical labels (Cohen’s κ **1.000**) with **zero** disputes. All **472/472** token labels and **56/56** message reference classes match the original scoring reference.

The original paired run froze both policies and an AI-assisted reference. ChatGPT filled the original R2 worksheet and took part in the two disputed decisions. The replacement human R2 confirmed the same final labels after that run. We recalculated the metrics against the two human reviews using the saved predictions. All public and synthetic scores reproduced. [Aggregate evidence and provenance](../release/evidence/holdout-56.json) · [KazNLP source and annotation conventions](https://arxiv.org/abs/2608.00581)

## Public messages

| Measure | Frozen 0.35 | Experimental borrowing rule |
| --- | ---: | ---: |
| False firm Mixed on monolingual messages | 3/24 | 3/24 |
| False firm Mixed on Kazakh-only messages | 2/17 | 2/17 |
| False firm Mixed on Russian-only messages | 1/7 | 1/7 |
| Firm Mixed recall | 15/16 | 15/16 |
| One-word switch recall | 10/11 | 10/11 |
| Possible switch on Kazakh-only references | 1/17 | 1/17 |
| Possible switch on mixed references | 1/16 | 1/16 |
| Resolved word coverage | 296/302 | 296/302 |

| Resolved word labels | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Kazakh | 189 | 0.989 | 0.952 | 0.970 |
| Russian | 113 | 0.939 | 0.947 | 0.943 |

The missed firm alert was a Kazakh word inserted into Russian. It received Possible switch. The 16 synthetic controls form a separate challenge set. The borrowing candidate downgraded one false firm alert and one correctly detected one-word switch in the controls. It changed zero public outcomes, so the submission uses 0.35. The frozen comparison used two policies built on 0.35. The [development comparison](COMPETITION_DEVELOPMENT.md) includes 0.20.

In the controls, all 12 romanized Kazakh words and all 12 unsupported Latin-script words received English highlights. The interface now advises checking those highlights. These controls illustrate a limitation and leave performance on everyday school chats and student speed open.

The locked model manifest SHA-256 was `d628e4fe4778161ab27d4ea424d63061d37ec9bdd0122828d19d1c88dc23a3aa`. The original annotation lock SHA-256 was `5613516d9fa5768784297d5b3bd4b7211d2f54801b6266d1b0dc77a949a904ed`. The [aggregate evidence](../release/evidence/holdout-56.json) also records the hashes of both human worksheets and the validated human reference.

## Scope of the follow-up

The private coordinator record under `artifacts/competition-independent/human-review/` holds the confirmed human worksheets, agreement and validated reference. The sample tests selected public comments and scripted controls. Evaluate future model changes on a disjoint sample with the comparison fixed in advance. A separate [student pilot](PHRASE_FINDING_PILOT.md) measures the phrase-finding workflow.
