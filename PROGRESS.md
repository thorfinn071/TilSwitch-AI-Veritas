# TilSwitch AI progress

**Current milestone** Word-only release verified from a clean Windows checkout. Human annotation of the KRCS split is pending.

**Workspace at intake** Empty Git repository with no commits and no project or ancestor AGENTS.md found. The request was a separate text attachment. The official brief was obtained from the organizer website.

## Completed planning work

| State | Work | Evidence |
|---|---|---|
| Complete | Workspace and instruction audit | No pre-existing application, data, model or implementation artifacts. Python 3.11.9 and Git available. |
| Complete | Verified the organizer's PDF, submission route and judging guidance | [Submission requirements](docs/HACKATHON_SUBMISSION.md). Working entrant access and form submission remain unchecked. |
| Complete | Read-only source and format checks | Tatoeba Kazakh export, Meta FLORES-200 archive, pinned author KRCS CSV and gated dataset metadata checked. No dataset staged or annotated in the repository. [Source audit](docs/ML_RESEARCH_PLAN.md#source-audit-and-choices) |
| Complete | Product, model and evaluation design | [Master plan](docs/MASTER_PLAN.md), [product](docs/PRODUCT_SPEC.md), [research](docs/ML_RESEARCH_PLAN.md) and [architecture](docs/ARCHITECTURE.md). |
| Complete | Schedule, QA, risks and submission strategy | [Backlog](TASKS.md), [testing](docs/TESTING_PLAN.md), [risks and gates](docs/RISKS_AND_DECISIONS.md), [submission](docs/HACKATHON_SUBMISSION.md). |

## Implementation on Nov 14, 2026

| Checkpoint | State | Evidence or remaining work |
|---|---|---|
| T01 entrant and scope | Implementation authorized | The user confirmed availability of a reviewer. Entrant registration and live submission access are unverified. |
| T02–T04 environment, sources and tokenizer | Complete locally | Python 3.11 lockfiles and dependency check. Verified Tatoeba, KRCS and FLORES downloads. Tested original offsets. |
| T05 review | Awaiting bilingual labels | Both validators found all expected rows. The 12 dev messages need 83 labels and reviewer codes. The 36 test messages need 260. [Instructions](docs/REVIEW.md) |
| T06 split preparation | Complete locally | 2,000 train and 350 each dev/test sentences per language. A repeat run reproduced split digests. FLORES preparation also passed. |
| T07–T08 models | Complete locally | Heuristic and both sparse logistic-regression models. Shipped word bundle `word-abf81e3da4` pending informal-dev model selection. |
| T09–T10 locked results | Mono complete, bilingual pending | Locked `mono-v1`, 1,050 held-out sentences. The continuation rerun reproduced the JSON summary and per-language CSV byte for byte. [Results and measured errors](docs/RESULTS.md) |
| T11–T12 runnable release | Verified locally | 31 tests and `pip check` passed. The clean checkout ran the CLI with `word-abf81e3da4`. Chrome verified the mixed example by keyboard, uncertainty, English, validation, clear and widths of 320–1,024 px. Human user acceptance is pending. |
| T13 package | Verified Windows candidate | The [write-up](README.md) lists the confirmed contributor, Nurmukhamed Sabit. [Credits](docs/DATA_AND_MODELS.md) and [frozen evaluation evidence](release/evidence/mono-v1.lock.json) accompany the model. The target repository is [TilSwitch-AI-Veritas](https://github.com/thorfinn071/TilSwitch-AI-Veritas). |
| T14–T16 submission and optional work | Pending | The designated entrant owns the submission and receipt. The optional video is deferred. |

The review check was made Saturday, Nov 14, at 21:44–21:48 Kazakhstan time (UTC+5). The working fallback can be submitted with the monolingual evidence while the reviewer completes KRCS. The first receipt target is Monday, Nov 16, at 00:30 and the organizer deadline is Monday at 09:59 (UTC+5). [Official submission instructions](https://highschoolhackathon.org/briefs)

For the next research run, finish the two [review sheets](docs/REVIEW.md), validate them and lock model and thresholds before scoring the holdout. Record the review coverage and run IDs with any new results.
