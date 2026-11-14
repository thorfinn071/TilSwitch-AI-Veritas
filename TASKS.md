# TilSwitch AI implementation backlog

Implementation is authorized and local work is tracked below. Use local Kazakhstan time (UTC+5), target the first receipt by **Mon Nov 16 at 00:30**, and stop submission changes by the official **09:59** close. The detailed clock and fallback budget are in the [master plan](docs/MASTER_PLAN.md#solo-schedule).

## How to run the backlog

- Keep one active implementation stage per solo work block. Team members can work independently where the task dependencies permit. Agree the contract before building dependents. Put the newest blocker, exact reproduction command and receipt location in [PROGRESS.md](PROGRESS.md).
- At the start of a block, run `git status --short --branch` and `rg -n 'Ready|Blocked|In progress' TASKS.md PROGRESS.md`. Choose the earliest P0 task with satisfied dependencies. Mark it In progress. Record a completed task only with its output and test evidence. Record a skipped task with the named gate and impact on published claims.
- Save a runnable checkpoint at T07 and T10. Give tasks that share a model or manifest the same lock ID. After tests score the holdout, freeze claim wording from saved predictions. New post-holdout model choices require a fresh independent holdout for claims about the change.
- Task deadlines are solo checkpoint deadlines, and estimates represent focused effort. The [team schedule](docs/MASTER_PLAN.md#small-team-schedule) overlaps tasks with independent work. If behind, apply [decision gates](docs/RISKS_AND_DECISIONS.md#gates-and-decisions) and update the task list.

## Milestones and dependency map

| ID | Status | Priority | Task / owner | Depends on | Estimate | Solo deadline |
|---|---|---|---|---|---|---|
| T01 | In progress | P0 | Confirm scope, entrant and delivery route / entrant | Implementation approved | 20 min | Sat Nov 14 17:50 |
| T02 | Complete locally | P0 | Bootstrap core and lock dependencies / engineer | T01 local authorization | 30 min | Sat Nov 14 18:50 |
| T03 | Complete locally | P0 | Pin sources and parser contracts / data owner | T01 local authorization | 30 min | Sat Nov 14 18:50 |
| T04 | Complete locally | P0 | Implement raw tokenizer and output contracts / engineer | T02 | 90 min | Sat Nov 14 20:20 |
| T05 | Awaiting bilingual labels | P0 | Freeze candidates and blind-review gold / bilingual lead | T03 and T04 for offsets. Draft text/policy can start during T03. | 195 min in three blocks | Sun Nov 15 12:05, texts frozen Sat 21:10 |
| T06 | Complete locally | P0 | Ingest, group, deduplicate and split / data owner | T03, T04 and T05 text snapshot. Labels can continue. | 90 min | Sat Nov 14 23:10 |
| T07 | Complete locally | P0 | Fit baseline/fallback and produce real CLI output / ML engineer | T06 | 105 min | Sun Nov 15 10:00 |
| T08 | Fitted, informal dev pending | P1 | Fit context variant and compare on dev / ML engineer | T07 and T05 dev labels | 45 min | Sun Nov 15 12:05 |
| T09 | Mono complete, KRCS pending | P0 | Lock and score held-out benchmarks / research lead | T05 gold for KRCS, T07, T08 complete or gated off | 90 min | Sun Nov 15 14:05 |
| T10 | Mono complete, KRCS pending | P0 | Interpret failures and lock reporting / research lead | T09 | 60 min | Sun Nov 15 15:05 |
| T11 | Complete locally | P0 | Wire Gradio or working demo fallback / product engineer | T07 for adapters, T09 for release model ID | 120 min | Sun Nov 15 17:20 |
| T12 | Local QA complete, user review pending | P0 | Clean checkout and user acceptance / QA owner | T10, T11 | 105 min | Sun Nov 15 19:05 |
| T13 | Fallback published and verified | P0 | Write, credit, publish and link-check / entrant and writer | Draft with T10, final after T12 | 160 min in two blocks | Sun Nov 15 22:15 |
| T14 | Ready for entrant | P0 | Submit and retain receipt / designated entrant | T13 | 35 min plus shared recovery buffer | Mon Nov 16 00:30 |
| T15 | Queued | P1 | Record optional video and verify update / presenter | T14 | 75 min | Mon Nov 16 08:30 |
| T16 | Queued | P2 | Defer stretch research until release permits / team | T14, separate scope and dataset | 2 h minimum per experiment | Defer beyond this event by default |

The solo plan treats T01–T04 as sequential. With two people, T02/T04 and T03/early T05 can overlap. T05 labeling and T07 fitting can overlap after T06 freezes texts and partitions. T11 can build against fixed development fixtures before T09 and must wire the real model before T12. Draft writing can run while experiments execute. T14 is owned by the entrant.

## Task contracts

### T01 Confirm scope, entrant and route

- **Work and required files** Confirm the start window, registered/eligible entrant, track, GitHub access or Colab fallback, whether a fluent reviewer is available and scheduled time. Record these as needed in `PROGRESS.md` without personal info. Create the implementation branch if authorized. Read the official PDF and [submission instructions](docs/HACKATHON_SUBMISSION.md).
- **Done and validation** Entrant can open the official form and knows who will submit. Check anonymous link route and actual deadline. No test submission. Select planned local release workflow and MVP branch. Check `git status`, Python 3.11 and write access.
- **Output and fallback** Timestamp/decision record. If competition access cannot be confirmed, the local project can still be built while the entrant checks official support. R01/R15.

### T02 Bootstrap core

- **Work and required files** `.gitignore`, `pyproject.toml`, both `requirements-*.lock.txt`, `conf/experiment.json`, package entry point and test scaffold. Install core in clean Python 3.11 environment first. Lock transitive packages for the verified platform. Add demo lock with compatible dependencies and check imports or leave that install for T11.
- **Done and validation** Core imports, `pip check` and CLI help work. Versions and lock digest recorded. Actual model and source files excluded from default tracking until release policy is followed.
- **Output and fallback** Installed/pinned CPU toolchain. If Gradio fails, keep core healthy and use CLI/Colab later. R12/R13.

### T03 Pin usable sources

- **Work and required files** `tilswitch/sources.py`, byte receipts under `data/raw`, source settings in `conf/experiment.json`, parser fixture and `tests/test_data.py`. Retrieve the Tatoeba detailed files and pair links and the pinned author KRCS release. Check fields and basic row/source counts. Have FLORES archive endpoint ready.
- **Done and validation** Read at least a valid row from all required sources using pinned provenance and parser checks. Verify content digests and usable inventory estimate. Timebox Tatoeba loading to 30 minutes.
- **Output and fallback** Source receipts/test fixture. Switch to FLORES if Tatoeba stalls and independently use authored gold if KRCS is unavailable or unsuitable. R02/R03.

### T04 Implement tokenizer and contracts

- **Work and required files** `tilswitch/types.py`, `tilswitch/text.py`, `tests/test_text.py` and fixture inputs. Implement input limits, Unicode spans, normalization, masks, script/neighbor eligibility, grouping and count semantics.
- **Done and validation** U01–U05 exercise raw reconstruction, offsets, token classes, Unicode/emoji and normalization. Verify deterministic status/neighbor fixtures here where possible. Prediction-aware U06/U07 checks finish at T07/T08. [Inference contract](docs/ARCHITECTURE.md#inference-contract)
- **Output and fallback** Validated spans API. If word tokenization needs a reduced rule set, record the changed boundary policy and re-export annotations before lock. R06/R08.

### T05 Freeze text and adjudicate gold

- **Work and required files** Put a minimal independent review export in `prepare.py` and write `data/review` manifests, label sheets and receipts. This export needs the dataset reader and tokenizer and can run before T06 completes training-source preparation. Screen and freeze selected KRCS IDs and authored texts, with dev/test assignments, for the overlap check. Pilot dev and measure labeling time. Later annotate test with predictions hidden, adjudicate and validate offsets/hash. Document second-review coverage and independence.
- **Done and validation** Attend to rubric v1 before final labels. Freeze original test text by Sat 21:10, finish gold by Sun 12:05. Meet the [support and fallback gates](docs/ML_RESEARCH_PLAN.md#targets-split-and-deduplication) or log the narrower study. M01/M02 verify source independence, fixed gold and cardinality.
- **Output and fallback** Independent dev/test gold, provenance and counts, plus workflow controls where time allows. Prioritize 12+36 real messages in the solo plan. If that gate cannot be met, use a locked speaker-authored set or the mono claim. R03/R06/R17.

### T06 Prepare data

- **Work and required files** `tilswitch/prepare.py`, `tilswitch/sources.py` if parser corrections are needed, `data/prepared`, split manifests and `tests/test_data.py`. Stream source records, filter and normalize fingerprints, resolve ID/parallel/duplicate/template groups, purge collisions with external content and sample by fixed hashes. Retain outcome and rejection counts. Fit nothing in this step.
- **Done and validation** M01, M02 and M04 pass. Verify disjoint groups and no contamination against originals or translation variants for external rows. Eligibility and actual examples per split recorded. Identical retrieval receipts reproduce the same split digest.
- **Output and fallback** Immutable prepared manifests and blind exports. Switch dataset per gate or simplify dedup search with explicit limit before locking. Invalid split integrity blocks evaluation. R02/R09/R10.

### T07 Baseline, word model and CLI

- **Work and required files** `features.py`, `train.py`, `infer.py`, `evaluate.py` dev path, `__main__.py`, core tests and versioned `artifacts/models`. Implement H and W. Fit W using train rows and align inference with the common tokenizer/guard. Run dev baseline and inference, save and reload W.
- **Done and validation** I01/I02, U06 and M03 smoke checks pass. CLI emits actual analysis using W. Predict a basic message in each of KK, RU and EN and one mixed message. Record timings and real dev counts. Keep a verified runnable checkpoint as the minimum deliverable.
- **Output and fallback** Baseline implementation, fitted W and dev trace. One documented solver retry or smaller deterministic cap if fitting fails before lock. Holdout remains unopened. R05/R12/R13.

### T08 Context learner and validation

- **Work and required files** `features.py`, `train.py`, `evaluate.py` and `tests/test_infer.py`. Add two fixed neighbor blocks to the same target features. Fit C with the same rows and hyperparameters. Score threshold grid and compare on reviewed dev. Write a release-candidate decision receipt.
- **Done and validation** U07 and fixture run pass. Check matched feature order and provenance. Choose C only under the predefined dev rule. Handle insufficient dev or early schedule slip by skipping C and selecting W.
- **Output and fallback** Fitted candidate, scores and decision, or documented cut. R05/R07/R15.

### T09 Freeze and evaluate

- **Work and required files** `tilswitch/evaluate.py`, `tests/test_eval.py`, `artifacts/runs/locked-eval.json`, evaluation predictions and metrics. Select threshold and release ID with dev outputs, assert hashes, then evaluate H/W/C where valid. Compute per-language, short-input and mixed-message metrics. If T08 finishes early, use its remaining time for paired uncertainty, coverage or latency receipts.
- **Done and validation** M01–M05 pass. No labels or scores from the final test enter fit or selection. Report supports, unresolved annotations, coverage and any unavailable comparison. Compute outputs from saved predictions. Keep release and locked evaluation IDs visible.
- **Output and fallback** Valid eligible runs and release candidate. If data support is below minimum, report descriptive cases or change to predeclared fallback without tuning on already seen test. R03/R09/R10.

### T10 Document evidence and errors

- **Work and required files** `docs/RESULTS.md`, referenced score tables and a side-by-side review sample. Review preallocated errors and note shared forms, boundary effects, borrowings, script, spelling and annotation. Derive the claims and limitations from evidence, including the fallback actually used.
- **Done and validation** Trace each published number and example back to predictions, support counts and the run ID. Include at least one actual failure with a reasonable explanation, and state whether each hypothesis was supported. Record missing strata and independence limits.
- **Output and fallback** Frozen claims, one released comparison and a reproducible results trail. No fabricated figure and no tuning. R05/R06/R10.

### T11 Wire a usable demo

- **Work and required files** `tilswitch/demo.py`, CLI launch and `tests/test_demo.py`. Build the single-message interaction and actual highlight/summary/segments. Startup validates bundle digest. Keep an operable model-inference route if UI components fail. Use `notebooks/demo.ipynb` only for the fallback or reviewer convenience.
- **Done and validation** I03, U09 and A01–A15 smoke expectations and failure states. Display uses actual release predictions and preserves literal text. Include readable labels, scoped help and no text logging.
- **Output and fallback** Local Gradio or verified CLI/notebook with plain-text labels. R08/R11/R12.

### T12 QA and release check

- **Work and required files** All tests plus a clean runtime receipt in `PROGRESS.md`. Verify workflow, appearance on a narrow screen, keyboard, dependencies, logs, UTF-8, artifact load and optional timing. Fix regressions before freezing release files.
- **Done and validation** I04 and the local model, evaluation and UX checks in the [definition of done](docs/TESTING_PLAN.md#definition-of-done) pass for the chosen path. T13 verifies public links and T14 records the receipt. If GUI fails by the deadline, switch to a verified CLI or notebook. Preserve exact run IDs for renderer-only fixes.
- **Output and fallback** Verified runnable release candidate. R08/R12/R14/R15.

### T13 Write and publish

- **Work and required files** `README.md`, `docs/DATA_AND_MODELS.md`, `docs/RESULTS.md`, allowed release artifacts, public GitHub link or viewable Colab. Use the official one-page outline, actual results, display-safe samples and complete credits.
- **Done and validation** Clone/open from a fresh environment, check anonymously viewable links, confirm release code and README route. Verify licensed artifacts and check the release for raw private data and secrets. Describe the exact released model and results.
- **Output and fallback** Release permalink, working instructions and one-page write-up. Focus on a verified alternate public route if publication fails. R01/R14/R15.

### T14 Submit the minimum complete package

- **Work and required files** Official Airtable submission from the entrant, required fields and an internal record in `PROGRESS.md` with sanitized receipt details. Verify team contribution fields and track. Submit by target time.
- **Done and validation** A confirmed timestamp, submitted version and public links are saved. If no confirmation, verify form condition and follow official support with both links. Never put entrant details in the public log.
- **Output and fallback** First valid receipt or a clear submission failure record. R01/R14/R16.

### T15 Add the optional video

- **Work and required files** A screen recording and share link, using [recording outline](docs/HACKATHON_SUBMISSION.md#demo-recording-plan). Record the actual release model and its observed successes/failures. Keep the available submission safe.
- **Done and validation** Playback works signed out, duration ≤2:00, same version as write-up, actual scores and no personal info. Resubmit only with a working replacement package and preserve the new receipt.
- **Output and fallback** Verified video link and current receipt. Omit if late. R14/R15/R16.

### T16 Consider stretch work

- **Work and required files** Decision in `PROGRESS.md`, a separate reproducible experiment config and new held-out data where needed. Consider romanization or calibrated out-of-scope rejection only after P0 and a receipt. Defer unless time covers new training, tests and release checks.
- **Done and validation** The baseline remains runnable, claims use new data, and signed-out submission path remains safe. Keep any post-deadline work outside the submitted version.
- **Output and fallback** Optional research result or documented deferral. R05/R09/R11/R15.
