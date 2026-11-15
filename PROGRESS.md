# TilSwitch AI progress

**Current milestone** The 0.35 Mixed-alert submission bundle is staged in `release/submission/model` with its aggregate evidence and a verification command. The public fallback is the original locked release at `988119e`. The entrant owns publication and confirmation. [Write-up and quickstart](README.md) · [Submission handoff](docs/HACKATHON_SUBMISSION.md)

**Workspace at intake** Empty Git repository with no commits and no project or ancestor AGENTS.md found. The request was a separate text attachment. The official brief was obtained from the organizer website.

## Completed planning work

| State | Work | Evidence |
|---|---|---|
| Complete | Workspace and instruction audit | No pre-existing application, data, model or implementation artifacts. Python 3.11.9 and Git available. |
| Complete | Verified the organizer's PDF, submission route and judging guidance | [Submission requirements](docs/HACKATHON_SUBMISSION.md). Working entrant access and form submission remain unchecked. |
| Complete | Read-only source and format checks | Tatoeba Kazakh export, Meta FLORES-200 archive, pinned author KRCS CSV and gated dataset metadata checked. No dataset staged or annotated in the repository. [Source audit](docs/ML_RESEARCH_PLAN.md#source-audit-and-choices) |
| Complete | Product, model and evaluation design | [Master plan](docs/MASTER_PLAN.md), [product](docs/PRODUCT_SPEC.md), [research](docs/ML_RESEARCH_PLAN.md) and [architecture](docs/ARCHITECTURE.md). |
| Complete | Schedule, QA, risks and submission strategy | [Backlog](TASKS.md), [testing](docs/TESTING_PLAN.md), [risks and gates](docs/RISKS_AND_DECISIONS.md), [submission](docs/HACKATHON_SUBMISSION.md). |

## Implementation on Nov 14–15, 2026

| Checkpoint | State | Evidence or remaining work |
|---|---|---|
| T01 entrant and scope | Public form reachable | The user confirmed availability of a reviewer. The official form displayed its Submit button in a signed-out Chrome session. Entrant registration and receipt remain unverified. |
| T02–T04 environment, sources and tokenizer | Complete locally | Python 3.11 lockfiles and dependency check. Verified Tatoeba, KRCS and FLORES downloads. Tested original offsets. |
| T05 review | Complete | One bilingual reviewer labeled 12 dev and 36 test messages. Both sheets validated, including the two final dev corrections. [Instructions](docs/REVIEW.md) |
| T06 split preparation | Complete locally | 2,000 train and 350 each dev/test sentences per language. A repeat run reproduced split digests. FLORES preparation also passed. |
| T07–T08 models | Complete | Heuristic and both sparse logistic-regression models. The KRCS dev gate selected `word-abf81e3da4` with a 0.10 margin threshold. |
| T09–T10 locked results | Complete | `mono-v1` scored 1,050 Tatoeba sentences. `krcs-v1` scored 36 human-reviewed messages with 252 Kazakh and Russian words. The tuned release scored 0.897 macro-F1 and falsely flagged five of seven Kazakh-only messages as mixed. [Results](docs/RESULTS.md) |
| T11–T12 runnable release | Verified locally | 31 tests and `pip check` passed. The CLI and Chrome verified the 0.10-threshold result. Chrome also verified keyboard analysis, mixed highlights, English, validation and clear at 360–1,024 px. Human user acceptance is pending. |
| T13 package | Ready for entrant | The [write-up](README.md) credits Nurmukhamed Sabit and includes the KRCS result and paired failure. The original word-only fallback was verified from an anonymous Windows clone of `e725a7e`. [Public code](https://github.com/thorfinn071/TilSwitch-AI-Veritas) · [Original fallback](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/e725a7e721c4ea156096f0693e94f7fd51c850f6) |
| T14–T16 submission and optional work | Ready for entrant | The designated entrant owns the submission and receipt. The optional video is deferred. [Official form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6) |

The KRCS run was locked and scored on Sunday, Nov 15, Kazakhstan time (UTC+5). The first receipt target is Monday, Nov 16, at 00:30 and the organizer deadline is Monday at 09:59 (UTC+5). [Frozen KRCS lock](release/evidence/krcs-v1.lock.json) · [Official submission instructions](https://highschoolhackathon.org/briefs)

On the local experiment branch, [informal Kazakh augmentation](experiments/README.md) improved word scores on development and scripted cases. It still produced five false mixed flags on the KRCS replay and lost one genuine one-word switch. The local release uses the original trained weights and an updated review policy.

The updated policy moved five of 87 firm mixed flags on single-language references to **Possible switch** in the 461-message KazNLP holdout. Both runs detected 159 of 161 clause-level mixed messages. The KRCS replay reduced firm false mixed flags from five to four of seven and retained 15 of 17 one-word switches. [Results and limits](docs/RESULTS.md#updated-switch-and-borrowing-policy-nov-15-2026)

All 33 tests passed in a clean package snapshot. The policy evidence reproduced, the wheel contained both browser assets, and Chrome verified the offline workflow, Copy, clipboard fallback, stale-result handling and responsive layout at 360–1280 px. The captioned clip is at `artifacts/demo-preview/tilswitch-demo.mp4` and runs 69 seconds. A student pilot and public release update are pending.

The local bundle now recognizes more spellings with distinctive Kazakh letters omitted and can put common one-letter words into a supported phrase. On the frozen FLORES-derived test, correct informal Kazakh labels rose from 841 to 941 of 1,200. The reviewed KRCS replay detected 16 of 17 genuine one-word switches and still flagged four of seven Kazakh-only messages as mixed. [Word-recovery results](docs/RESULTS.md#informal-spellings-and-short-words-nov-15-2026)

The updated bundle and evaluation reproduced byte-for-byte for the inference assets, all 35 tests and 500 Unicode offset checks passed, and Chrome verified the full Russian phrase copy and the **Informal Kazakh** example. The refreshed 69-second clip is at `artifacts/word-recovery-demo/tilswitch-demo.mp4`. The public update and student pilot are pending.
