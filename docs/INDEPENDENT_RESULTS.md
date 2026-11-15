# Locked 56-message diagnostic of the 0.35 release

The batch contains 40 selected public KazNLP comments and reviews and 16 authored controls. The scoring recipe, both policies and the 56 references were frozen before the single paired run. The numbers below describe an **AI-assisted diagnostic**.

The archived review record overstated human provenance. R1 returned a filled worksheet and reported labeling from their own reading. That report was relayed in the project chat. The available record does not independently establish who produced R1's labels. ChatGPT generated R2's labels from the blank worksheet and guide. The source conversation explicitly identified R2 as AI. The downloaded R2 file, imported file and locked copy match by SHA-256.

The sheets agreed on **381/383** lexical spans (Cohen’s κ **0.990**) before resolution. This is agreement between worksheets involving AI. The two disputed spans took R1's recorded labels after ChatGPT as R2 saw those labels and agreed. [Aggregate evidence and corrected provenance](../release/evidence/holdout-56.json) · [KazNLP source and annotation conventions](https://arxiv.org/abs/2608.00581)

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

The locked model manifest SHA-256 was `d628e4fe4778161ab27d4ea424d63061d37ec9bdd0122828d19d1c88dc23a3aa`. The annotation lock SHA-256 was `5613516d9fa5768784297d5b3bd4b7211d2f54801b6266d1b0dc77a949a904ed`. The aggregate results above use the references from that lock.

## Human review handoff

The blank worksheet and guide are in the local sprint worktree under `artifacts/competition-independent/reviewer-packet/`. Send these two files privately for a label audit. Collect a TSV directly from a Kazakh–Russian bilingual reviewer who has seen neither previous labels nor model outputs. Ask how they use both languages and whether they labeled without AI or translation tools. Verify R1's authorship and process separately. If it cannot be verified, collect a second human worksheet too. Assign reviewer codes, preserve the original returns and resolve disagreements between verified people with predictions hidden. A comparison with the cached predictions would audit the references on this already-scored batch.

For a fresh blind test, select a disjoint sample. Freeze the models, thresholds and comparison rules. Collect both human reviews, record the agreement before adjudication and freeze the resolved references before the paired run. The original 56-message lock and score receipt are archived.
