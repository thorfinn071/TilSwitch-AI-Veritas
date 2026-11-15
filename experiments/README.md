# Informal Kazakh experiment

This candidate addresses two sources of false Russian highlights: informal spellings that omit distinctive Kazakh letters, and loan nouns that take Kazakh endings. The contest release stays on the original word model. The candidate is available locally for comparison.

## Try the candidate

From the repository root in PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m tilswitch demo --bundle artifacts/runs/informal-v1/model
& .\.venv\Scripts\python.exe -X utf8 -m tilswitch analyze --bundle artifacts/runs/informal-v1/model --text 'Кун ашык далага шыгамыз'
```

For that example the reference is Kazakh for all four words. The contest model marks `Кун` and `далага` as Russian and flags the message as mixed. The candidate marks all four words as Kazakh. It still flags `Асханаға позже барамыз` as mixed and marks only `позже` as Russian. It marks `Колонкамен` as uncertain in `Колонкамен ән қойып көрдік`, where the contest model marks it as Russian. It also introduces a false mixed flag on `Стикерпак отправили без подписи`, a Russian example. These are actual model outputs on invented inputs.

## How the candidate was selected

Training used the original Tatoeba training split plus 1,848 distinct Kazakh spellings with simplified letters and 152 scripted inflections of loan nouns. The added forms avoid exact matches to words already in training. The suffix idea is similar to a [KRCS translation augmentation](https://arxiv.org/html/2503.20007v1#S4.SS1); this experiment uses its own examples and a word classifier. The added forms are approximate and were not reviewed by a linguist. No KRCS annotations were used as training examples.

Both models use the contest word margin of 0.10. Model selection used the 12 human-labeled KRCS development messages and 12 separate [authored development cases](informal-cases.jsonl). The candidate had to preserve development Kazakh recall, word coverage and detection of mixed messages, without increasing false mixed flags on the human development set or losing one-word switches on the authored development cases. The lock also tested labeling weak singleton evidence as **Possible switch** while retaining the highlights. This extra margin made no difference on either development set, so it stayed off in the candidate.

## Results

| Comparison | Contest model | Candidate |
|---|---:|---:|
| Human development, Kazakh/Russian word macro-F1 (81 words) | 0.816 | 0.910 |
| Human development, Kazakh words correctly labeled (47 words) | 32 | 42 |
| Human development, false mixed flags (3 single-language messages) | 3 | 2 |
| Scripted challenge, Kazakh/Russian word macro-F1 (85 words) | 0.903 | 0.920 |
| Scripted challenge, words assigned a language (85 words) | 79 | 78 |
| Scripted challenge, false mixed flags (12 single-language messages) | 4 | 3 |
| Scripted challenge, mixed detected (8 mixed messages) | 8 | 8 |
| Scripted challenge, one-word switches detected (4 messages) | 4 | 4 |

The 20 challenge cases were scored after the dev choice was locked. Both the messages and their references were AI authored. They are checks of specific behavior, with 41 Kazakh and 44 Russian words. They are too small and too closely tied to the experiment to establish performance on real school chats.

The previously evaluated 36-message KRCS test is a diagnostic replay. Word macro-F1 rose from 0.897 to 0.910. Kazakh F1 was 0.933 → 0.943 on 190 words; Russian F1 was 0.861 → 0.877 on 62 words, though Russian recall fell from 59/62 to 57/62. Word macro-F1 on the 18 short messages was 0.850 → 0.886. At switch boundaries it was 0.887 → 0.880 on 76 words. Both models assigned a language to 245/252 words and correctly flagged 26/29 mixed messages. Both falsely flagged 5/7 Kazakh-only messages. Genuine one-word switches detected fell from 15/17 to 14/17. This single-reviewer sample contains no Russian-only messages.

The separate Tatoeba replay scored 0.961 → 0.959 on 1,050 monolingual sentences with source-language word labels, using the 0.10 margin for both models. These are weak labels. The earlier base scores in [the release report](../docs/RESULTS.md) used a zero margin.

The candidate stays local. Its higher word score does not establish a reduction in false flags on real text, and the loss of a one-word switch matters to the product. A new bilingual review on a disjoint sample with both Kazakh-only and Russian-only messages would be needed to confirm a release improvement.

## Reproduce the local run

Use the original prepared splits and validated KRCS reference files described in [the review workflow](../docs/REVIEW.md). Place the frozen bundle from the [original release](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/988119e483ffd6b8c26e9543a98e7ec044e592d0/release/model) in `artifacts/models/krcs-release`. Run the training command only if `artifacts/models/word-informal` does not already exist. Use a new path for the experiment run.

```powershell
& .\.venv\Scripts\python.exe -m tilswitch train --model word --informal
$run = 'artifacts/runs/informal-recheck'
& .\.venv\Scripts\python.exe -m experiments.informal lock --out $run
& .\.venv\Scripts\python.exe -m experiments.informal score --out $run
& .\.venv\Scripts\python.exe -m experiments.informal replay --out $run
```

The local `artifacts/runs/informal-v1` folder contains the development lock, the candidate bundle `word-informal-5fe83080f9`, the challenge summary, the replay and a Chrome check. The trained bundle and raw review files stay out of Git. A second fit reproduced the weights and vocabulary. The candidate passed CLI and Chrome checks for the corrected informal spelling, a one-word switch and an uncertain word. The updated test suite passed 32 tests.
