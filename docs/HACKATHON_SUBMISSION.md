# TilSwitch AI hackathon submission plan

The current submission write-up is the GitHub README with the locked KRCS results. Nurmukhamed Sabit is the solo entrant. The initial Nov 14 package remains available at its original commit. [Public code](https://github.com/thorfinn071/TilSwitch-AI-Veritas) · [Current write-up](../README.md) · [Results](RESULTS.md) · [Credits](DATA_AND_MODELS.md) · [Initial write-up](https://github.com/thorfinn071/TilSwitch-AI-Veritas/blob/e725a7e721c4ea156096f0693e94f7fd51c850f6/README.md)

## Official requirements and source precedence

The organizer PDF governs the track and document format. The official submission page and FAQ govern the form and support route. Checked against the PDF on Nov 14, 2026. Use the latest organizer communication if a participant instruction changes.

| Authority | Requirements for TilSwitch |
|---|---|
| Project Briefs §§2–3 | A team of one to three high-school students. All project work takes place within the window. Include actual AI/ML in the main function. Use public/synthetic data or the team's own work and only use another person's messages with permission. Credit datasets, pretrained models, AI and coding tools, libraries and tutorials used. Report unseen test results, a simple baseline and at least one failure. Team members must be able to explain their work. |
| Project Briefs §4.4 | Enter AI + Languages. Give results per language or accent. Show real examples with model predictions alongside the reference. Public material or the team's own writing is allowed. Real-speaker review is valuable for judging and the gold policy. The track starter is sentence-level Tatoeba language ID and adding original work is required when building from it. The suggested script counts, sample sizes and package choices are starter guidance. |
| Project Briefs §5 | Working, viewable GitHub repo or Colab with saved outputs, approximately one-page write-up, one selected track, complete team details and source links. Video is optional, capped at two minutes and shared by unlisted YouTube or public-view Drive link. One team member submits. The latest submission before the deadline is judged. |
| Project Briefs §6 | Four named dimensions are technical quality, impact, creativity and clarity. The PDF supplies no weights for these four headings. The separately published Judges page gives a Round 1 points rubric that also names Testing and Honesty. Apply both sources as written, and avoid inferring weights for the PDF's four headings. |

[Official Project Briefs](https://drive.google.com/file/d/15tYD48XRmCgWbk1_lLDtc8lebi6qm-4-/view?usp=sharing) · [Submission instructions](https://highschoolhackathon.org/briefs) · [FAQ](https://highschoolhackathon.org/faq) · [Judging page](https://highschoolhackathon.org/judges)

**Times** US ET kickoff Sat Nov 14 00:00 and hard close Sun Nov 15 23:59. Kazakhstan UTC+5 kickoff Sat Nov 14 10:00 and hard close Mon Nov 16 09:59. Target the first valid submission by Mon **00:30**. A late-start fallback targets Mon **06:30**. Record actual early submission and latest update times. [Roadmap](MASTER_PLAN.md#solo-schedule)

The official Airtable form displayed its Submit button in signed-out Chrome. The designated entrant submits through the form and keeps the receipt. If the form fails on submission, email the organizer immediately with both verified links. The official deadline still governs. [Official submission form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6) · [Organizer instructions](https://highschoolhackathon.org/briefs)

## Public package

| Artifact | Requirement and content |
|---|---|
| Public GitHub repo or viewable Colab | Link to a versioned release/commit when practical. Clean setup path, Python lock, inference entry and one reproduction command sequence. Verify the old link stays valid after updates. Keep raw or identifying input excluded. |
| README write-up | Serve the approximately one-page competition write-up. Use the organizer's template below and link to extended docs for details. Include one minimal quickstart and one actual output comparison. GitHub README is the selected one official write-up format. |
| DATA_AND_MODELS.md | Combine dataset register, correction/exclusion rules, source credits, license obligations, split/hashes and a model card with intended use, hardware/config, known error conditions, scope and private fields kept out of the release. Attribute permitted displays. Where allowed, publish the external gold as source IDs, token offsets and labels with its attribution and share-alike terms, and let the reproduction command fetch the pinned source text. Where rights or privacy prevent this, publish eligible aggregate outputs, mask cases as needed and state exactly which checks reviewers can reproduce. |
| RESULTS.md and run receipts | Combine experiment instructions, actual per-language results, baseline table, counts, error examples, reproducibility and limits. Record run/model/data IDs, class support, coverage and origin. Reference the exact release. Keep unrun rows labeled pending until measured. |
| Optional demo media | A single ≤2 min screen recording of the real model. Verify shared playback in a signed-out window and links inside the write-up. |
| Private submission fields | Track and the full name, email and school of every contributor for the form. Follow the official write-up team-name field where appropriate. Keep emails, raw chat data and unnecessary student identifiers out of the public repo. |

### One-page write-up outline

1. **TilSwitch AI**, **Languages** and team name(s) in the organizer's format.
2. **The problem** in two or three sentences. A student who reads one school-chat language more comfortably needs to isolate the part to ask about or translate.
3. **What we built** in three or four sentences. Describe a real input/output loop, Cyrillic Kazakh and Russian, English support, and the exact release path the judge can run.
4. **What we added** in two or three sentences. Build on the language-ID starter with a word-level workflow and independent bilingual annotation of an informal sample. Describe any context comparison or loanword analysis that actually happened. Identify the specific starter and credit related research.
5. **How it works** in four or five lines. List sources, actual train/dev/test sizes after exclusions, the script rule, character features, context setting and abstention policy.
6. **Results** with one small table. Rows for evaluated models, columns for source, word macro-F1, language-specific scores and word/message support, with links to full tables. Include one exact input, expected labels, the actual baseline/candidate output and plausible cause of a failure. Give coverage and sample origin so the result can be interpreted.
7. **What we'd do next** in one or two concrete items, for example independent bilingual review or a properly held-out romanization dataset.
8. **Sources** with dataset, third-party model, tool and tutorial hyperlinks, including Codex if used. Keep contributor and library notices in the linked credit file when longer than a line.

## Demo recording plan

Record after the first receipt. Use a clean browser window with the release model loaded locally. Close unrelated tabs and notifications, zoom for readability and keep the output from real inference. Pick the clearest allowed held-out failure by the error-analysis policy after evaluation. Use an authored demonstration message for the main live paste. Avoid private chats, unrelated account info and raw annotation spreadsheets on screen.

| Timestamp | Speaking and screen outline |
|---|---|
| 00:00–00:15 | “A school group message can switch languages mid-sentence. A student who reads Kazakh or Russian more easily wants to find just the phrase to ask about.” Show one message. |
| 00:15–01:15 | Paste the authored school example and press Analyze. Point to two actual highlights, the words used for the mixed decision and the phrase to copy. Use a second short case to show what the app does when evidence is weak. |
| 01:15–01:45 | Explain that each word supplies short character patterns and that the experimental classifier also sees neighbors. Show the result table with real baseline/model values and the size/origin of the held-out set. Show expected and predicted labels on the same short example. |
| 01:45–01:56 | Name one actual weakness and a realistic next data collection or evaluation step. End at about 1:56 for export margin. |

Record at readable resolution, turn captions on if easy, play back the exact upload signed out, and submit the optional link only while the previous complete submission remains safe.

## Judging strategy

| Official PDF dimension | Evidence we can produce |
|---|---|
| Technical quality | A working offline input/output path. Comparable methods trained and scored on fixed manifests. Word and message denominators made explicit. Test errors traceable to example IDs. This also addresses the Judges page's testing and honesty item. |
| Impact | A full school-message → highlight → select phrase interaction with a student or teammate. Explain the current manual alternative and the observed friction in that small task. |
| Creativity | A measurable switch-boundary and borrowing question on Kazakh–Russian beyond sentence-level ID. Credit existing corpora and token-level work. Show which design choices originated with the team. |
| Clarity | One user, one live paste, one simple rule and one evidence table with a concrete failure. Prepare to explain in plain words how train/test isolation and abstention work. |

The highest-value additions after the minimum baseline work are a stronger bilingual review sample, a controlled context ablation on unchanged data, and a clear paired failure comparison for a borrowed word or a one-word switch. Allocate a remaining hour to those before polish or deployment.

## Submission checklist

- [x] Public GitHub code with read permissions, pinned write-up, runnable instructions and actual demo output.
- [x] README write-up with word and language-level results, a paired reference and failed prediction, original contribution and sources.
- [ ] Required track and names, emails and schools for all real contributors, as they should appear on certificates. One designated entrant submits for the team.
- [x] Credits for the datasets, tools, libraries and prior work. The release includes model files and aggregate evidence and keeps raw data and review sheets local.
- [ ] Optional video link works signed out and runs no more than 2:00. If absent, a working demo path still exists in code.
- [x] Verified the fallback code, write-up, results and credits links signed out and ran the CLI and tests from an anonymous clone.
- [ ] Submit early through the official form. Save time, receipt or confirmation and exact links. Follow the official contact route immediately if the form fails.
- [ ] Resubmit only a verified improvement before close. Recheck links and keep the latest valid confirmation. [Testing definition of done](TESTING_PLAN.md#definition-of-done)
