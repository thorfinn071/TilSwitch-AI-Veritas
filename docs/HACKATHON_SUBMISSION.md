# TilSwitch AI hackathon submission handoff

Use the README in the same version as the submission bundle for the one-page write-up. Nurmukhamed Sabit is the solo entrant. The latest verified public fallback is the original locked KRCS release at `988119e`. The 0.35 submission bundle is staged locally for the entrant. [Proposed write-up](../README.md) · [Results](RESULTS.md) · [Credits](DATA_AND_MODELS.md) · [Public fallback](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/988119e483ffd6b8c26e9543a98e7ec044e592d0)

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

The official Airtable form displayed its Submit button in signed-out Chrome on Nov 15. The designated entrant submits through the form and keeps the receipt. If the form fails on submission, email the organizer immediately with both verified links. The official deadline still governs. [Official submission form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6) · [Organizer instructions](https://highschoolhackathon.org/briefs)

The first visible Git commit was made Nov 14 at 22:05 in Qyzylorda, after the 10:00 kickoff. The intake record describes an empty repository, and local source and evaluation timestamps are consistent with the competition window. The entrant should confirm the coding window and project provenance before accepting the organizer's rules. Git and file timestamps cover only the records examined. [Development record](../PROGRESS.md) · [48-hour coding rule](https://highschoolhackathon.org/faq)

## Public package

| Artifact | Requirement and content |
|---|---|
| Public GitHub repo or viewable Colab | Use the commit link carrying `release/submission/model`, its aggregate evidence, and the pinned dependencies. Check the code and README links in a signed-out window. Keep raw or identifying input excluded. |
| README write-up | Use the README at that same commit as the one-page write-up. It identifies the original KRCS evaluation and the later cutoff-selection comparison. |
| DATA_AND_MODELS.md | Combine dataset register, correction/exclusion rules, source credits, license obligations, split/hashes and a model card with intended use, hardware/config, known error conditions, scope and private fields kept out of the release. Attribute permitted displays. Where allowed, publish the external gold as source IDs, token offsets and labels with its attribution and share-alike terms, and let the reproduction command fetch the pinned source text. Where rights or privacy prevent this, publish eligible aggregate outputs, mask cases as needed and state exactly which checks reviewers can reproduce. |
| RESULTS.md and run receipts | Combine experiment instructions, actual per-language results, baseline table, counts, error examples, reproducibility and limits. Record run/model/data IDs, class support, coverage and origin. Reference the exact release. Keep unrun rows labeled pending until measured. |
| Optional demo media | A single ≤2 min screen recording of the real model. Verify shared playback in a signed-out window and links inside the write-up. |
| Private submission fields | Track and the full name, email and school of every contributor for the form. Follow the official write-up team-name field where appropriate. Keep emails, raw chat data and unnecessary student identifiers out of the public repo. |

### One-page write-up outline

1. **TilSwitch AI**, **Languages** and team name(s) in the organizer's format.
2. **The problem** in two or three sentences. A student who reads one school-chat language more comfortably needs to isolate the part to ask about or translate.
3. **What we built** in three or four sentences. Describe a real input/output loop, Cyrillic Kazakh and Russian, English support, and the exact release path the judge can run.
4. **What we added** in two or three sentences. Build on the language-ID starter with a word-level workflow and bilingual review. Describe the context comparison and explain that the cutoff-selection labels were AI-drafted and confirmed by one reviewer. Identify the specific starter and credit related research.
5. **How it works** in four or five lines. List sources, actual train/dev/test sizes after exclusions, the script rule, character features, context setting and abstention policy.
6. **Results** with one small table. Rows for evaluated models, columns for source, word macro-F1, language-specific scores and word/message support, with links to full tables. Include one exact input, expected labels, the actual baseline/candidate output and plausible cause of a failure. Give coverage and sample origin so the result can be interpreted.
7. **What we'd do next** in one or two concrete items, for example independent bilingual review or a properly held-out romanization dataset.
8. **Sources** with dataset, third-party model, tool and tutorial hyperlinks, including Codex if used. Keep contributor and library notices in the linked credit file when longer than a line.

## Two-minute demo script

Launch `python -m tilswitch demo --bundle release/submission/model` and open the local app in a clean browser window. The examples in the demo are authored. The results page credits the sources for the evaluation. [Run instructions](../README.md) · [Results](RESULTS.md)

| Time | On screen | Narration |
|---|---|---|
| 00:00–00:18 | Open **School announcement**. | “A school group message can start in Kazakh and give the meeting location in Russian. If I need help with just the location, I first have to find that phrase.” |
| 00:18–00:42 | Select **Analyze** and **Copy** beside **в актовом зале**. | “TilSwitch highlights the languages and keeps the spelling and punctuation as written. I can copy the complete Russian phrase, including the one-letter preposition. The analysis runs on this computer.” |
| 00:42–01:02 | Analyze **One-word switch**, then **Possible borrowing**. | “Here, *позже* is the Russian word. In the borrowing example, *пропускпен* has a possible Kazakh ending, so the app asks me to review it.” |
| 01:02–01:24 | Show the method paragraph in the README. | “Kazakh and Russian share Cyrillic. We trained logistic regression on short character patterns in Tatoeba words. The word-only model passed our development gate. The app uses extra checks for some spellings, short words, and borrowings.” |
| 01:24–01:45 | Show the 60-message comparison. | “We chose the new alert cutoff on this set. False firm alerts fell from four to two across 26 single-language references. Both settings detected all 20 mixed messages, including 10 one-word switches.” |
| 01:45–02:00 | Analyze `Salem qalaysyn` and point out the English label. | “Romanized Kazakh can be mistaken for English. We still need independent school-chat testing. Today the app gives students a specific phrase to ask about.” |

Record at readable resolution and verify signed-out playback of the exact upload. Add an optional clip only if it uses the submission bundle and runs at most two minutes.

For a short student pilot, use two comparable authored announcements with the location phrase in a different language from the rest. Ask classmates to find the phrase explaining where to go. Show one message as plain text and one with the live highlights, then alternate the order across participants. Record task completion and elapsed time for each, without names.

## Judging strategy

| Official PDF dimension | Evidence we can produce |
|---|---|
| Technical quality | A working offline input/output path. Comparable methods trained and scored on fixed manifests. Word and message denominators made explicit. Test errors traceable to example IDs. This also addresses the Judges page's testing and honesty item. |
| Impact | A full school-message → highlight → select phrase interaction with a student or teammate. Explain the current manual alternative and the observed friction in that small task. |
| Creativity | A measurable switch-boundary and borrowing question on Kazakh–Russian beyond sentence-level ID. Credit existing corpora and token-level work. Show which design choices originated with the team. |
| Clarity | One user, one live paste, one simple rule and one evidence table with a concrete failure. Prepare to explain in plain words how train/test isolation and abstention work. |

The highest-value additions after the minimum baseline work are a stronger bilingual review sample, a controlled context ablation on unchanged data, and a clear paired failure comparison for a borrowed word or a one-word switch. Allocate a remaining hour to those before polish or deployment.

## Submission checklist

- [x] Public fallback at `988119e` is reachable signed out.
- [x] The proposed README reports the original KRCS results, the cutoff-selection result, an observed error and credits.
- [x] The local submission bundle contains weights, vocabulary, spelling evidence, policy and aggregate results.
- [ ] Publish the exact staged tree and verify the commit and README links signed out. Check that the published manifest matches the local release.
- [ ] Select **AI + Languages** and enter the entrant's full name, school and email privately in the form. Confirm the competition-window and contribution requirements.
- [ ] Use the pinned code link and the README at that commit as the single write-up. If adding a video, check that anyone with the link can play it and that it is at most 2:00.
- [ ] The entrant submits through the official form and records the exact links, time and confirmation. Use the official support route if submission fails. [Organizer instructions](https://highschoolhackathon.org/briefs)

## Publish the verified tree

Use the local handoff patch at `artifacts/submission-handoff/tilswitch-submission.patch` from the development workspace. From the repository root, apply it to a clean worktree based on the public fallback commit. Choose an unused branch and sibling folder if these names are already in use.

```powershell
$patch = (Resolve-Path -LiteralPath 'artifacts/submission-handoff/tilswitch-submission.patch').Path
git worktree add -b codex/tilswitch-submission ..\tilswitch-submission 988119e483ffd6b8c26e9543a98e7ec044e592d0
if ($LASTEXITCODE -ne 0) { throw 'Could not create the submission worktree.' }
Set-Location ..\tilswitch-submission
git apply --index $patch
if ($LASTEXITCODE -ne 0) { throw 'The submission patch did not apply.' }
git diff --cached --stat
git write-tree
```

Compare the tree ID with the local handoff receipt. Run the [README quickstart](../README.md#what-we-built) in that worktree. The verification command should print a 0.35 Mixed-alert cutoff. After reviewing the staged changes, the entrant can commit and push this branch.

```powershell
git commit -m "Prepare TilSwitch AI hackathon submission"
git push origin HEAD
git rev-parse HEAD
```

Use the printed commit ID in `https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/<commit>` for code and `/blob/<commit>/README.md` on the same repository for the write-up. Verify both links signed out and check that `release/submission/model/manifest.json` at that commit matches the local manifest. Then follow the checklist and save the organizer's confirmation.
