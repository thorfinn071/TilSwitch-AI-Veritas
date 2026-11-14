# TilSwitch AI testing and quality assurance plan

Keep code correctness fixtures distinct from ML evidence. All tests below are future acceptance work. Use authored text and miniature local source files. Reuse the inference path that will be shipped. Save model/run IDs and outputs in [progress](../PROGRESS.md) and any actual evaluation receipts.

## Automated acceptance

| ID | Level and target | Inputs and expected result |
|---|---|---|
| U01 | Normalization | NFC and decomposed equivalents map to the same normalized word. Check uppercase and combine all nine distinctive Kazakh letters. Apostrophe and dash variants become equal only in feature strings. Pasted characters remain intact. |
| U02 | Token spans | Table-driven inputs with a Kazakh combiner, emoji composed with ZWJ, emoji skin tone, multi-space, tabs and CRLF, an apostrophe, hyphen and punctuation, a URL followed by a comma and `12:30`. Offsets are half-open and ordered. `raw[start:end]` equals every token and full gap reconstruction is byte-identical after UTF-8 encoding. |
| U03 | Script and masks | One-letter words, apostrophes, repeated Latin and Cyrillic lookalikes, mixed alphanumerics, Chinese text, emoji keycaps, a hashtag, handle, URL, email and digit strings. Confirm expected neutral or review reason. Script predicates never transform the display. |
| U04 | Validation | Empty, whitespace-only, non-string, invalid Unicode at CLI/file input, exactly 1,000 code points and 1,001. Valid punctuation only returns neutral-only. User text is preserved in the field on validation errors and CLI exits with the specified status. |
| U05 | Grouping | Same predicted label over horizontal spaces merges. Different labels, punctuation, emoji, unknown words and newlines have the defined boundary behavior. Preserve text order, spaces and exact spans. |
| U06 | Prediction summaries | With known test scores or fixed labels, cover all message statuses, counts, lexical denominator, null neutral-only shares and language order/absence. Check script mismatch and top-two margin below, at and above threshold. Verify estimator class order with shuffled fixture classes. |
| U07 | Context extraction | Left and right slots use the expected neighbors. Beginning/end, newline, sentence-ending punctuation, masks and unsupported spans produce absent slots. Compare dev/train/inference extraction. Test duplicated or subsampled target rows with full-message context. |
| U08 | Source schema and mappings | UTF-8 and optional BOM, bad TSV count/unknown code, Tatoeba `kaz/rus/eng`, FLORES member names and aligned IDs, normal quoted KRCS multiline row, empty ID, missing translation and known label enum. Failed download or changed digest produces a safe, reported failure. |
| U09 | HTML/rendering | Bare angle brackets, ampersand, multiline and curly quotes display as text in a standard result. Neutral/gap substrings and label row order reconstruct raw message. |
| I01 | Offline fixture pipeline | Tiny sources → validate/group → prepare → train word LR → save → evaluate → load → infer. Confirm deterministic row/label output and every class has support. Repeat with context if built. |
| I02 | Version and bundle protections | Stable IDs, independent release directories, invalid sha, missing bundle, incompatible metadata/schema and stage failure. Confirm a failed write cannot replace the previous usable release and CLI returns an actionable error. |
| I03 | End-to-end UI callback | Invoke the real callback with test bundle and known text. The analysis and renderer agree on original text, labels, segment order, counts and weak/empty feedback. In a manual local UI check submit two messages in order and ensure stale scores are cleared. |
| I04 | Clean launch | Fresh Windows Python 3.11 venv and a clean checkout. Follow only the public instructions. Run `pip check`, one test command, CLI and optional Gradio from a new process. If using Colab, run top to bottom in a fresh CPU runtime and check published saved output and access. |
| M01 | Leakage and splits | Assert stable row IDs and parent IDs, group/exact/near-dup isolation, known parallel links, and external originals/translation purge. Check dev/test labels excluded from fit and vectorizer vocabulary fit only on training words. Test leakage guard on a controlled duplicate that would otherwise cross. |
| M02 | Label integrity | Counts by source, split, origin and class. Check gold tokenizer offsets, reviewer/status enum, ambiguous and neutral handling and every primary dataset/metric denominator. Validate required support before training lock. |
| M03 | Metrics | Hand-worked small cases with wrong language, abstention, mixed true/false, empty denominators and indeterminate gold. Scores retain unknown predictions as errors on known gold. Verify precision/recall/F1 under class imbalance and binary support warnings. |
| M04 | Reproducibility | Run prepare twice on same source receipts/config, compare split and artifact data hashes after excluding timestamps. Run inference twice and compare labels, spans and counts exactly, numeric scores within 1e-8 in one pinned environment. Verify outputs from saved predictions reconstruct the displayed tables. |
| M05 | Frozen manifest | Score command rejects missing schemata, gold digest mismatch and a candidate/threshold mismatch. A new evaluation run writes new output and records the reason. Test split never selects thresholds. |

Run fast fixtures after each stage using `python -m pytest -q`. Keep tests at the metadata and behavior boundaries. ML accuracy tests derive conclusions from locked benchmark runs. Never fix a fixture label by choosing what the current model predicts.

## User acceptance

These are authored **smoke examples** and may illustrate the intended behavior when reviewed. Exclude them and close variants from final test sets. Some are ambiguous on purpose. A bilingual reviewer should label phrases and confirm the reference expectations before any judge-facing presentation. Exact statistical evaluation cases come from the frozen review set.

| Case | Input | Design expectation | Review |
|---|---|---|---|
| A01 Kazakh | Мен ертең сабаққа барамын. | Preserve original and show KK where supported. | Speaker labels lexical reference. |
| A02 Russian | Мы завтра встречаемся после уроков. | Show RU evidence and valid offsets. | Speaker labels lexical reference. |
| A03 English | Please bring your notebook tomorrow. | Show EN evidence, no invented confidence. | Review reference. |
| A04 KK/RU | Сәлем, завтра сабақ нешеде начинается? | KK, RU, KK, KK, RU as target. Any actual mismatch is visible. Group the two adjacent KK words. | Speaker validates word/use policy. |
| A05 RU/EN | Завтра принеси notebook, пожалуйста. | Russian evidence plus an English insertion under the token policy. | Review the use of notebook for this example. Smoke only. |
| A06 KK/RU/EN | Ертең сабақ бар, не забудь: bring your notebook. | Three distinct supported spans if predicted. Review tags if any uncertain. | Speaker validates boundaries. Smoke only. |
| A07 Ambiguous | да | Preserve the word and show the model's real response. If it assigns a language, include it as an ambiguity failure when reviewed. | Speaker marks ambiguity under policy. |
| A08 Informal spelling | Каласын, завтра келесин бе? | Test Cyrillic Kazakh typed without distinctive letters and a Russian insertion. Surface uncertain words. | Speaker adjudicates intended meaning, do not assume exact predicted labels. |
| A09 Borrowing | Файлды жібердім. | Gold treats an integrated loan as Kazakh. Track a false mixed flag if the model produces one. | Speaker validates the marked borrowing. |
| A10 Named entity, digits, emoji | Аружан, сабақ 12:30 🙂 | Name may be incorrectly labeled and is neutral in gold. Comma, time and emoji remain neutral in the app. | Speaker marks name. Neutral-mask behavior is a contract check. |
| A11 Unsupported and neutral | 你好 👋 42 | Chinese tokens fall to review, followed by neutral emoji/number. | Smoke guard. No claim for unseen Latin-script languages. |
| A12 No lexical input | !? 123 🙂 | Status is neutral-only and shares are null. | Smoke guard. |
| A13 Romanized Kazakh | Salem, qalai? | Check scope note and log actual output. Latin text may resemble English. | Speaker confirms that romanization is outside MVP support. |
| A14 Neutral links and mixed script | https://example.org, @test! cабаq | Preserve characters. Link and handle neutral, letter lookalike word sent to review. | Smoke guard. |
| A15 Long multiline | A 1,000-code-point fixture ending with a grapheme and newline | Input and wrapping remain usable, output relates to the submitted text. A 1,001-code-point case rejects. | Smoke guard. |

## UX and manual release verification

- Perform the exact student flow in [Product specification](PRODUCT_SPEC.md). Confirm input label, keyboard order, one analysis per action, real result, text selection and copying for the chosen phrase, clear behavior and an example that actually fails or abstains.
- Use 360 px, 768 px and desktop widths. Check keyboard focus and no horizontal overflow with long text, 200% zoom, contrast against actual colors and status readability in a screen reader or the accessibility tree. Copy the output text and compare it to original, respecting neutral spacing and line breaks.
- Use one fresh Python process for cold load and at least 30 representative short and near-limit requests for warm latency if time permits. Record platform, package versions and p95. Reuse the known bundle. Collect conventional diagnostics only and keep input private.
- Have a team member without local cache use the public setup directions if someone is available. If solo, reinstall from a fresh checkout and report that review was local. Test every public link signed out and cross-check the exact release against the submitted link.

## Definition of done

- [ ] The intended user completes paste, analyze and select/copy. The local browser, CLI or notebook release works on real inputs. The write-up identifies the shipped path.
- [ ] A fitted ML artifact performs the core task and a genuinely simple baseline runs through the same eligibility/split contract.
- [ ] Ordered Unicode slices, labels, summary states, recovery and critical leak tests pass. Unsupported/ambiguous inputs have documented behavior and test coverage.
- [ ] Locked train/dev/test receipts and real predictions generate per-language and short-input results, code-switch findings where supported, side-by-side real output and a failure example.
- [ ] Origin, class and message counts, gold policy, model version, environment, seeds, limits and unresolved weaknesses are documented. Any fallback claim changes across README, UI, demo and submission.
- [ ] A clean checkout verifies the reproducible command path, shareable data and licenses are respected, and links/credits are visible without login.
- [ ] One eligible entrant submits the correct track, accessible code and one-page write-up, source credits and accurate team information. Preserve a receipt from before the deadline. The optional video meets the two-minute cap and shows actual model output. [Submission checklist](HACKATHON_SUBMISSION.md#submission-checklist)
