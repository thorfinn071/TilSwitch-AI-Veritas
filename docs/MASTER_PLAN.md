# TilSwitch AI master plan

**Track** AI + Languages, Veritas AI International High School Hackathon 2026

**Planning scope** One local text demo with a reproducible word-level evaluation and a working command-line fallback. See the [progress log](../PROGRESS.md) for the implemented release and remaining review and submission work.

## Decisions to build around

- **User and moment** A Kazakhstani student who can read one language in a school group chat more comfortably than the other. When a short message mixes Kazakh and Russian, the student pastes it, sees which phrases need translation or help and selects the particular phrase to take to a translator or classmate. [Product specification](PRODUCT_SPEC.md)
- **Competition contribution** Extend the organizer's sentence-level Tatoeba example to word spans in informal Kazakh–Russian messages. Measure when nearby words improve the prediction and when uncertain words still need review. Show a correct result and a failure beside the reference labels. Position this as a weekend prototype and evaluation for a specific student workflow. Prior Kazakh–Russian token-level research exists. [Official Project Briefs, §§3, 4.4](https://drive.google.com/file/d/15tYD48XRmCgWbk1_lLDtc8lebi6qm-4-/view?usp=sharing) · [KazRusCSW](https://github.com/liminovna/KazRusCSW)
- **Model** TF-IDF character features from the current word plus separately weighted features from its immediate left and right words, with L2-regularized multinomial logistic regression. Fit on the CPU. Use the same learner with only current-word features as the first checkpoint, the default fallback and the context ablation. A script-and-letter heuristic is the simple baseline. [Architecture](ARCHITECTURE.md)
- **Evidence** Use Tatoeba for weakly labeled train and development data and a source-internal monolingual test. Annotate a blind, held-out sample of independent KRCS originals. Score speaker-authored chat scenarios and optional artificial mixtures independently. [ML research plan](ML_RESEARCH_PLAN.md)
- **Delivery** Build a one-message Gradio demo and keep the CLI usable from the start. Publish working code on public GitHub, with an approximately one-page README as the write-up. Capture a video only after the first submission has a receipt. [Submission plan](HACKATHON_SUBMISSION.md)

## Feasibility audit

| Question | Finding and decision |
|---|---|
| 1. Can we identify words accurately in a weekend? | A working closed-set prototype for Kazakh Cyrillic, Russian Cyrillic and English is feasible. Real-chat accuracy and open-world reliability are unmeasured. Make the Kazakh–Russian comparison the central claim and English a secondary language. |
| 2. What is hardest? | Kazakh and Russian share Cyrillic. Shared words, name handling, loanwords, colloquial spellings and mislabeled source text can dominate errors. Text boundary errors also corrupt both visualization and scoring. |
| 3. Which datasets actually exist? | Downloaded and inspected the Tatoeba Kazakh export (4,577 rows), Meta's FLORES-200 (997 dev and 1,012 devtest sentences per relevant language), and the authors' KRCS release (618 complete rows before deduplication). Quantities after cleaning remain unknown. |
| 4. Are these informal? | Tatoeba is contributed example and translation text with some conversational lines. FLORES is translated reference prose. KRCS gives colloquial source messages selected for translation research. It is a plausible external test of register shift, with sampling bias. |
| 5. Is there labeled Kazakh–Russian code-switching data? | The KazRusCSW-G-T card documents about 3,000 manually tagged Telegram/YouTube comments. Anonymous data access is gated and the public card has no explicit license. KRCS is open and provides source texts and translations. Its originals need fresh word labels. KazNLP supplies document-level labels under a different switching guideline. |
| 6. Can synthetic mixing help? | Test provenance-tracked phrase splices only if the required work is secure. A training augmentation trial needs independent dev evidence. Report metrics by origin. |
| 7. What makes evaluation credible? | Freeze a target, labels, slices, split hashes and comparison rules before viewing predictions for held-out cases. Keep author/source/template clusters together. Score errors and abstentions, show support, and report limitations of small or single-reviewed samples. |
| 8. Are word characters enough? | Useful for spelling, suffixes and distinctive letters. Shared forms, short spellings and loanwords can have identical input features under distinct labels. Use token-only LR as the empirical comparison. |
| 9. When is context useful? | A neighbor can disambiguate a shared form or an informal spelling. A neighbor across a switch can also pull the prediction toward the wrong language. Measure both cases with the same split and tokenization. |
| 10. What counts as a word label? | Label productive borrowings by current use, names and nonlanguage spans as neutral in gold, and genuine unresolved cases separately. Runtime flags obviously unsupported scripts and abstains on weak evidence. A human gold policy is stricter than what a three-class model can infer. |
| 11. Is Latin Kazakh in scope? | Cyrillic Kazakh is supported. Ambiguous Latin strings can overlap with English, names and other languages. Romanized Kazakh and mixed-script morphology need distinct training and test evidence. |
| 12. What is too risky? | Cut transformer fine-tuning, API dependencies, public hosting as a prerequisite, scraping, translating, adding languages, batch analytics and a custom web stack. |

Facts, observed download counts, licenses and fallback routes are maintained in the [ML research plan](ML_RESEARCH_PLAN.md). Assumptions about registration, bilingual review and execution time are tracked in [Risks and decisions](RISKS_AND_DECISIONS.md).

## MVP and release decisions

| Tier | Deliverable and acceptance |
|---|---|
| 1 — Mandatory | Analyze a single message locally, highlight supported words and contiguous spans, show language counts and detect mixed messages. Handle empty text, neutral text and uncertain words explicitly. Fit at least the token-only ML model. Evaluate it against the simple baseline on the frozen data, including per-language results, short inputs and an external informal sample or the documented authored fallback. Aim for a small independent set of mixed and non-mixed student-workflow controls. Provide a reproducible CLI, runnable interface or notebook, tests, one-page write-up and public submission links. |
| 2 — Competitive | Fit and evaluate the context model under the locked comparison. Ship it if validation favors it under the predefined rule. Expand speaker-reviewed edge cases for borrowing and switching, record independent annotator agreement and report coverage versus error and latency. Each addition needs a measured result, a count or a user-tested interaction. |
| 3 — Stretch | Romanized Kazakh, improved unknown-language rejection, a separate transformer experiment, bilingual UI, deployment or batch tools. Start after the first valid receipt and only with enough headroom for full verification and documentation. Use new evaluation data for any new claim. |

**Fallback on model quality** Release the token-only model with the same interface, honest failure analysis and the context comparison if it ran. If mixed routing is unreliable, use descriptive language evidence and manual review in the UI. If annotation stalls, switch to the locked authored set or release a monolingual research prototype with exploratory mixed highlighting and explicitly limit the claim. If the browser stack fails, present the same inference through the CLI and a viewable notebook if available. Verify the working route before publishing. [Exact gates](RISKS_AND_DECISIONS.md)

## Execution order

| Checkpoint | Tasks | Exit condition |
|---|---|---|
| G0 — Inputs | T01–T03, early T05 in parallel where possible | Confirm the submission route, lock data source choices, install pinned dependencies and draft the review protocol. |
| G1 — First working model | T04, T05 text freeze, T06, T07 | Freeze the annotation sample before preparing clean grouped splits. Verify tokenizer, saved token-only LR, a baseline score on dev and an end-to-end CLI result. Tag the actual working commit. |
| G2 — Evidence | T05, T08–T10 | Finish blind labeling, lock configuration and manifest hashes, run the held-out evaluation, save raw predictions and record at least one real failure. |
| G3 — Release candidate | T11–T13 | Run acceptance checks, reproduce the public launch path from a clean copy and verify links and credits. |
| G4 — Submitted | T14 | One designated entrant sends the verified version and saves the confirmation. A version with a video is optional. |

The implementation critical path runs through **T01 → T02/T03 → T04 → T05 text freeze → T06 → T07 → T09 → T10/T11 → T12 → T13 → T14**. **T05 gold must finish before T09**. T08 is the optional model branch. The exact task contracts and solo deadlines live in the [backlog](../TASKS.md).

## Solo schedule

Use Kazakhstan local time (UTC+5). Kickoff was **Sat Nov 14 at 10:00**. Hard close is **Mon Nov 16 at 09:59**. The **Sat 17:30** working start leaves **40 h 29 min** to the close. Plan to submit by **Mon 00:30**, leaving **9 h 29 min** for recovery or an update. Move any work completed before the rounded start out of the first block. If implementation starts later, use the cut rules below.

| Local time | Work and deadline |
|---|---|
| Sat 17:30–18:50 | T01–T03. Verify entrant access and public publishing route, start installs, fetch sources and pin the chosen paths. |
| Sat 18:50–21:10 | T04 and first T05 block. Build the tokenizer and contracts, draw blind samples and pilot the gold policy on dev alone. |
| Sat 21:10–21:40 | Dinner and break. |
| Sat 21:40–23:10 | T06. Validate ingestion, group and split corpora, and export a provenance and counts receipt. |
| Sat 23:10–Sun 00:15 | Continue T05. Label validation and start the locked test batch with predictions hidden. |
| Sun 00:15–07:45 | Sleep, 7 h 30 min. |
| Sun 07:45–08:15 | Breakfast. |
| Sun 08:15–10:00 | T07. Train the fallback, run the heuristic and token LR on dev, save the bundle and prove CLI inference. |
| Sun 10:00–12:05 | Finish T05 and attempt T08. Finish review before showing test predictions. Fit context LR using the same training rows. |
| Sun 12:05–12:35 | Lunch. |
| Sun 12:35–15:05 | T09–T10. Freeze choices, score the holdouts, analyze errors and create tables from saved predictions. Lock the CLI at this milestone. |
| Sun 15:05–15:20 | Break. |
| Sun 15:20–17:20 | T11. Gradio wiring and actual-result smoke tests. |
| Sun 17:20–19:05 | T12. Clean environment, integration QA and recoverable fixes. |
| Sun 19:05–19:35 | Dinner. |
| Sun 19:35–21:20 | T13 write-up, provenance, credits, examples and run instructions. |
| Sun 21:20–Mon 00:30 | T13 publishing and incognito checks, T14 receipt. Includes roughly 1 h 40 min of recovery and upload buffer inside this block. |
| Mon 00:30–07:15 | Sleep or rest after first receipt. Preserve the submitted release. |
| Mon 07:15–08:30 | Optional T15 video and resubmission only if the release still passes. Target last planned update at 08:30. |
| Mon 08:30–09:59 | Deadline buffer for a material issue with the submission. Verify receipt/links and use the organizer's submission support route if needed. |

The 31 hours before first receipt include **19 h 35 min of focused tasks**, **1 h 40 min of recovery buffer**, **2 h 15 min of meals and breaks** and **7 h 30 min of sleep**. The solo plan assumes basic Python and Git competence and one fluent Kazakh–Russian reviewer for the gold data.

## Small-team schedule

Use the same breaks, sleep window and hard stop. Assign one integrator to own the branch and one entrant to own submission. Roles can overlap. Additional contributors must be eligible team members who actually work on the entry.

| Local deadline | Work for two | Adjustment for three |
|---|---|---|
| Sat 18:50 | A owns runtime, data downloads and form check. B checks the KRCS path, drafts annotation policy and gets speaker coverage. Agree contract fields together. | C drafts a clickable flow on paper, checks form/publication and starts test cases from the agreed contract. |
| Sun 00:15 | A finishes tokenizer, data splits and fixture loader. B pilots and labels the independent gold sample. Allocate an agreed batch for second review if both are bilingual. | C builds UI with fixture-only responses for development and writes acceptance tests. Switch all demo entries to actual predictions before release. |
| Sun 12:05 | A fits fallback and context models. B locks annotations, reviews ambiguity and validates group isolation independently. | C integrates model loader, tests original-text reconstruction and prepares the first write-up draft. |
| Sun 15:05 | A scores frozen benchmarks. B checks confusions and claim wording. | C independently runs the CLI, Gradio and accessibility checks on a fresh environment. |
| Sun 20:30 | A and B check a versioned public release and submit together after QA. | C records a video after receipt if the material is ready. A handles any integration fix. |
| Mon 08:30 | Last planned update if the first package benefits from it. | Same deadline and link verification. |

## Late-start cuts

1. Preserve the blind external sample, simple baseline, token learner, runnable entry and required submission fields. Drop all Tier 3, then synthetic training, alternative detectors, extra charts and optional slices beyond the specified short/no-diacritic diagnostics.
2. If the token-only checkpoint misses Sun 10:00 by over an hour, skip T08 while getting a runnable model. Reduce annotation to the documented minimum with support shown. If the release fails at Sun 19:05, prioritize the CLI/notebook route and first receipt.
3. If authorization comes after Sat 20:00, switch to the fast path immediately. Allocate around 1 h to setup/source checks, 2 h to tokenizer and split pipeline, 1 h 45 min to fallback ML plus CLI, 2 h to annotation, 1 h 30 min to frozen evaluation and failures, 1 h 30 min to a minimal GUI or checked notebook, 2 h 30 min to QA/write-up/publication and 1 h to submission. Put a 7 h 30 min sleep block and 2 h 15 min of breaks into the remaining time first. Target submission by Mon 06:30 at the latest for this path. If that fit still fails, invoke the monolingual or notebook fallback by the model and data gates.

Start each work block from the [active backlog](../TASKS.md), update [progress](../PROGRESS.md) with receipts, and use the [definition of done](TESTING_PLAN.md) before publication.
