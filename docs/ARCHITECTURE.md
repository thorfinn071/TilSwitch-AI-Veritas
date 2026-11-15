# TilSwitch AI software architecture

The implementation uses the contracts below with three delivery changes. Model bundles store JSON and numeric NPZ arrays, the app renders escaped original slices in a Gradio HTML component, and initial releases live under `release/model`. The actual commands are in [README](../README.md), [results](RESULTS.md) and [review instructions](REVIEW.md).

## Runtime and stack

Use Windows x64 and **CPython 3.11** for the reference run. The host exposes Python 3.11.9 and Git. Use standard-library CSV, bz2, tarfile, hashlib, json, argparse, logging and urllib. Avoid a data-frame dependency in core. Use NumPy and SciPy for sparse features, scikit-learn for training and scoring, regex for Unicode grapheme/script matching, pytest, and joblib for local artifacts.

| Option | Choice and engineering cost |
|---|---|
| Gradio Blocks | Primary demo. Native text area, buttons, progress and highlighted-text output share the Python process and model bundle. Build a result table so the demo stays interpretable if the suggested highlight component has visual or screen-reader problems. |
| Streamlit | Feasible alternative with text-area/form support and sanitized HTML, but needs a custom renderer and extra rerun-state work here. The team should use the CLI/notebook fallback if Gradio setup stalls. |
| React | Adds a JS build and API or model port, and duplicates text-boundary handling. Reserve for a future product. |
| Colab | Optional executable reviewer route with saved outputs. Reuses the package and pinned data or bundle. Test from a fresh runtime. It can display the CLI outputs as text if browser sharing is unavailable. |

Gradio accepts categorized raw spans and optional custom colors. Give it substring/label tuples to keep offset math on the Python side. In the pinned Gradio version, set `analytics_enabled=False` on Blocks and pass theme, CSS, server name and share settings to `launch()`. Check highlight and copying behavior with ordinary and multiline text. [Pinned HighlightedText](https://github.com/gradio-app/gradio/blob/gradio%406.32.0/gradio/components/highlighted_text.py) · [Pinned Blocks](https://github.com/gradio-app/gradio/blob/gradio%406.32.0/gradio/blocks.py) · [Streamlit HTML](https://docs.streamlit.io/develop/api-reference/text/st.html) · [scikit-learn model persistence](https://scikit-learn.org/1.7/model_persistence.html)

**Initial version pins to verify in T02** Python 3.11, scikit-learn 1.7.2, NumPy 2.2.6, SciPy 1.15.3, joblib 1.5.2, threadpoolctl 3.6.0, regex 2025.9.18 and pytest 8.4.2. Add Gradio 6.32.0 only to the demo lock. These have published packages for the reference interpreter. The combined install is a future task. Record resolved transitive packages. A Windows or Colab lock change must pass dependency check, clean run and artifact compatibility verification. If a UI dependency conflicts, keep the core environment and pivot early.

## Planned repository

Only the Markdown planning files exist in the planning phase. The tree defines future paths and contracts.

~~~text
veritas/
├── README.md                      # Public short write-up and demo command
├── TASKS.md
├── PROGRESS.md
├── .gitignore                     # venv, caches, raw data, private rows, generated runs
├── pyproject.toml                 # pytest settings and supported interpreter
├── requirements-core.lock.txt     # Reproducible core/test environment
├── requirements-demo.lock.txt     # Includes core and locked Gradio dependencies
├── conf/
│   └── experiment.json            # Schema, limits, seeds, source choices and policy
├── tilswitch/
│   ├── __init__.py
│   ├── __main__.py                # Local CLI and exit codes
│   ├── types.py                   # Validated records and label/status enums
│   ├── text.py                    # Unicode tokenizer, normalization, segmentation
│   ├── sources.py                 # Download/verify, parse and license/source manifest
│   ├── prepare.py                 # Validation, dedup, grouping, splitting and export
│   ├── features.py                # Report token rows and sparse feature matrices
│   ├── train.py                   # W/C fitting and versioned bundle metadata
│   ├── infer.py                   # Shared model/heuristic analysis and summaries
│   ├── evaluate.py                # Lock check, per-case predictions and score tables
│   └── demo.py                    # Local Gradio callback and presentation adapter
├── tests/
│   ├── fixtures/                  # Authored text, tiny TSV/CSV and manifest fixtures
│   ├── test_text.py
│   ├── test_data.py
│   ├── test_infer.py
│   ├── test_eval.py
│   └── test_demo.py
├── data/                         # Runtime ignored cache
│   ├── raw/
│   ├── prepared/
│   └── review/                    # Blind exports, annotation records and adjudication
├── artifacts/                     # Generated immutable bundles and run receipts
│   ├── models/
│   └── runs/
├── docs/
│   ├── MASTER_PLAN.md
│   ├── ML_RESEARCH_PLAN.md
│   ├── PRODUCT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── TESTING_PLAN.md
│   ├── HACKATHON_SUBMISSION.md
│   ├── RISKS_AND_DECISIONS.md
│   ├── DATA_AND_MODELS.md         # Published provenance, licensing, model card, limits
│   └── RESULTS.md                # Actual reproduction commands, scores and errors
└── notebooks/
    └── demo.ipynb                 # Optional only, visible outputs
~~~

### Module interfaces

The signatures below are implementation contracts. JSON schema versions are explicit. Thread a resolved Config into pure functions and the CLI, with one config load and readable validation errors. Use stable dataclasses/enums to keep downstream alignment clear.

| Module | Functions and responsibilities |
|---|---|
| types | `MessageRecord`, `Token`, `GoldToken`, `LanguageSegment`, `Analysis`, `RunConfig`. Validate label membership, text length/hash, raw span invariants, schema version and unique IDs. Runtime language output is `kk/ru/en/unk/neutral`. |
| sources | `fetch_source(source, cache_dir) -> SourceReceipt`. `iter_records(receipt) -> Iterator[MessageRecord]`. Bounded fetch, content hash, quote-aware parsing, declared columns, license fields and structured exclusion counts. Mask metadata for export. Never auto-download during inference. |
| text | `tokenize(raw) -> list[Token]`, `normalize_word(surface) -> str`, `group_segments(raw, predictions) -> list[LanguageSegment]`. Only normalized feature text is transformed. |
| prepare | `prepare(receipts, cfg, out_dir) -> DatasetReceipt`, `make_review_batch(receipt, split) -> ReviewBatch`, `validate_review(review_rows, manifest) -> FrozenGoldReceipt`. Groups and split manifests travel with every row. When a correction changes eligibility, rebuild and issue a new receipt. |
| features | `word_rows(messages) -> Iterator[WordRow]`, `build_features(rows, vectorizer, use_context) -> csr_matrix`. Rows contain target and optional immediate neighbor feature strings, document ID and offsets. Target row sampling is applied before a train fit with the full message retained for context. |
| train | `fit_model(train, cfg, mode) -> Bundle` and `save_bundle(bundle, dir) -> ModelReceipt`. Mode is `word` or `context`. Only train rows reach fit. Save class order and validation-independent fit settings. Lock inference thresholds in a release/evaluation run manifest. |
| infer | `load_bundle(path, expected_sha) -> Bundle`, `analyze(raw, model_or_heuristic, policy) -> Analysis`. Per UI process, cache the checked bundle once. H and both learned models share the tokenizer, guards, status logic and labels. |
| evaluate | `score(frozen_inputs, comparator_set, manifest) -> RunReceipt`, `make_report(run) -> table files`. Dev command records candidate policies. Test command requires a lock with dataset/model hashes and writes predictions and metrics by dataset and unit. No fit calls on this path. |
| demo | `analyze_for_ui(raw) -> (highlights, status_text, segment_rows)` and `build_ui(bundle) -> Blocks`. Test the adapter offline. Test the local browser flow manually. |
| __main__ | Parse command arguments, validate local paths, load config, run the intended stage. `0` success, `2` invalid input/config/schema, `1` operational or missing-bundle error. Errors go to stderr, machine-readable analyze output to stdout. |

## Inference contract

1. **Validate.** Input is a Python str of at most 1,000 Unicode code points with non-whitespace content. Treat malformed JSON/Unicode at the input boundary as an input error. Accept Unicode letters and combining marks, numerals, newlines and emoji. Empty input is an input error, and punctuation-only input produces a valid neutral-only result.
2. **Tokenize the original.** Scan left to right with Unicode-aware matcher rules and a final `regex` `\X` extended-grapheme fallback. Retain whitespace as gaps. Match precedence is URL/email, mentions/hashtags, complete emoji sequences (including digit keycaps), structured time/number, lexical words, then remaining graphemes. Lexical words are runs of Unicode letters and attached marks, with internal apostrophes or hyphens only between letters. Treat alphanumeric runs such as `abc123` as single unsupported lexical candidates. The numeric pattern must not consume digits attached to letters. Trim trailing sentence punctuation from a URL as its own span. Format marks, emoji and punctuation receive neutral. Keep every span as [start,end) in Python Unicode code points. Raw slices and gaps reconstruct the exact text. A future JS consumer can convert to UTF-16 offsets or use the raw substrings directly.
3. **Normalize per word.** NFC, casefold and NFC again. Map internal apostrophe/dash variants to canonical ASCII forms for feature text. Preserve all supported letters including ә, ғ, қ, ң, ө, ұ, ү, һ and і. No transliteration, accent stripping or confusable replacement. Link/number text is never an ML feature. Skip token normalization for display.
4. **Make sparse features.** Apply the vectorizer shared across positions to the target and at most one adjacent eligible supported-script word per side. The neighbor search crosses horizontal spacing and a comma or similar nonterminal punctuation. Stop at newline, `.`, `!`, `?`, Unicode ellipsis, unsupported lexical tokens or neutral masks (URLs, numbers, handles). A deterministic single-letter guard keeps one-letter words out of inference and context. Unsupported or missing neighbor uses a zero row. Enforce the same function in train and inference. [Fit settings](ML_RESEARCH_PLAN.md#fit-specification)
5. **Classify and guard.** Neutral masks and punctuation have no probability. Mixed Cyrillic/Latin, non-target scripts, alphanumeric words and one-letter tokens return `unk` with a reason. For other candidates run H, W or C. For learned models guard empty target feature rows and script/class contradictions, then apply the frozen margin. Chosen labels may still confuse a proper noun or unsupported language that shares a script. Gold named-entity policy is evaluated as a limitation. A real person can override an uncertain result by selecting the text and asking for help.
6. **Create segments.** Merge consecutive lexical tokens with the same display label when the intervening raw characters are horizontal whitespace only. Any neutral token or newline breaks a segment. Keep unknown spans individually visible or merge them under `unk` with each token's reason preserved. Output lexical segments (including unk) in order and send every neutral/gap substring with no highlight. Compare concatenation against the raw input.
7. **Summarize.** The bundle can ask for review on a possible Kazakh borrowing. When the model contains the spelling lookup, inference can also recover an attested Kazakh spelling and assign a common single-letter word using nearby evidence. The raw offsets and text are preserved. Count `kk,ru,en,unk,neutral` from the resulting tokens. With at least two accepted languages, return `mixed` when both have enough support under the bundle policy and `possible_switch` otherwise. Return `single` when one label covers all lexical words, `needs_review` when the remaining lexical words include unknowns, and `neutral_only` when there are zero lexical words. Set `primary_language` for `single` and `has_unknown` whenever unk is present. The language and unknown share denominator is `kk+ru+en+unk`. With zero lexical words, shares are null. [Released word evidence](RESULTS.md#informal-spellings-and-short-words-nov-15-2026)

Illustrative result contract using the requested target behavior. Values below are specification fixtures.

~~~json
{
  "schema_version": 1,
  "model_id": "example-only",
  "offset_unit": "unicode_code_point",
  "text": "Сәлем, завтра сабақ нешеде начинается?",
  "tokens": [
    {"start": 0, "end": 5, "text": "Сәлем", "label": "kk", "reason": null},
    {"start": 5, "end": 6, "text": ",", "label": "neutral", "reason": "punctuation"},
    {"start": 7, "end": 13, "text": "завтра", "label": "ru", "reason": null},
    {"start": 14, "end": 19, "text": "сабақ", "label": "kk", "reason": null},
    {"start": 20, "end": 26, "text": "нешеде", "label": "kk", "reason": null},
    {"start": 27, "end": 37, "text": "начинается", "label": "ru", "reason": null},
    {"start": 37, "end": 38, "text": "?", "label": "neutral", "reason": "punctuation"}
  ],
  "segments": [
    {"start": 0, "end": 5, "text": "Сәлем", "label": "kk"},
    {"start": 7, "end": 13, "text": "завтра", "label": "ru"},
    {"start": 14, "end": 26, "text": "сабақ нешеде", "label": "kk"},
    {"start": 27, "end": 37, "text": "начинается", "label": "ru"}
  ],
  "counts": {"kk": 3, "ru": 2, "en": 0, "unk": 0, "neutral": 2},
  "lexical_count": 5,
  "shares": {"kk": 0.6, "ru": 0.4, "en": 0.0, "unk": 0.0},
  "status": "mixed",
  "primary_language": null,
  "has_unknown": false
}
~~~

## Artifact and environment management

- A bundle directory holds `model.joblib` (fitted TF-IDF and LR), `metadata.json` (classes, train manifest hash, package versions, code commit, schema, feature configuration and expected file hash), and `policy.json` (threshold and wording choice from the evaluation lock). Put the three SHA-256s and release ID in an adjacent manifest. Validate compatibility and expected bytes before joblib loading. Only accept a locally built artifact or one obtained through the verified project release. The app accepts text. [Model persistence](https://scikit-learn.org/1.7/model_persistence.html)
- Write generated artifacts to a temporary output directory and rename atomically on success. Fail clearly if a run ID already exists. Keep core model data and threshold/version metadata together so a failed retry leaves the previous release runnable. Record Python, OS/platform, numeric libraries and git commit. Prefer a CLI startup check on model/artifact failures.
- Log stage name, elapsed time, sizes, row counts, reasons, config hash and exit status. Avoid raw chat strings, user identities and paths to secrets in distributable logs. Local inference keeps no text logs and launches Gradio on 127.0.0.1 with sharing disabled and analytics disabled. Enforce the 1,000-code-point limit in Python. Any manual HTML fallback must escape user text or use a plain component. Use no server accounts, databases, API key or file upload.
- Keep dependencies for the CLI viable even if setup of the demo module fails. Use conventional sparse CSR layout. Record peak memory and warm/cold inference times on the actual benchmark. Package speed and size remain to be measured.
- Pinned source revisions and material used in displays can be published with the relevant upstream attribution and permissions. Tatoeba rolling snapshots may need a permitted fixed snapshot for exact retraining. If the exact bytes cannot be shared, document the gap and provide a release-local inference route if permitted. Model and source license decisions are independently logged.

## Planned Windows commands

The commands describe the completed interface. Implement and test them in the backlog order. Use a 64-bit shell with UTF-8 input files. Redirected console output can use `-X utf8` or a PATH/environment appropriate to PowerShell. Path arguments below are relative to the repo.

~~~powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-core.lock.txt
& .\.venv\Scripts\python.exe -m pip check

& .\.venv\Scripts\python.exe -m tilswitch fetch --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch review export --dataset krcs --split dev --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch review export --dataset krcs --split test --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch prepare --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch review validate --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch train --model word --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch train --model context --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch evaluate --phase dev --config conf/experiment.json
& .\.venv\Scripts\python.exe -m tilswitch evaluate --phase test --lock artifacts/runs/locked-eval.json
& .\.venv\Scripts\python.exe -m tilswitch release --lock artifacts/runs/locked-eval.json --out artifacts/models/release
& .\.venv\Scripts\python.exe -X utf8 -m tilswitch analyze --bundle artifacts/models/release --text 'Сәлем, завтра сабақ нешеде начинается?'
& .\.venv\Scripts\python.exe -m pytest -q

& .\.venv\Scripts\python.exe -m pip install -r requirements-demo.lock.txt
& .\.venv\Scripts\python.exe -m pip check
& .\.venv\Scripts\python.exe -m tilswitch demo --bundle artifacts/models/release
~~~

The experiment config contains schema_version, source_set, raw/prepared/review/artifact directories, split/annotation seeds, eligibility limits, active models, feature settings and threshold grid. Initial review export prepares one shared KRCS candidate inventory across dev and test, then emits the requested split. Later exports reuse those IDs. Use dataset authored for the locally written batch and add that text inventory before prepare freezes the training split. The dev evaluator writes the candidate decision and both dev reports. Add frozen gold, source, split, config, policy and fitted-model digests to the reviewed lock before starting test evaluation. The release command copies the selected fitted model, checked metadata and frozen policy to a new output directory. The CLI can use a word checkpoint bundle for T07 before the final lock. A verified release supports offline analysis after setup. If a team chooses Spaces later, validate current runtime limits and anonymous access, retain the local route and explain server processing. [Work order](../TASKS.md)
