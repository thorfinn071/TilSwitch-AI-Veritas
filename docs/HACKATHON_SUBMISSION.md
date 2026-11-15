# TilSwitch AI submission and practice scripts

Use the contest commit on `codex/tilswitch-veritas-final`. Its README is the English write-up. It launches `release/submission/model` with the verified 0.35 alert cutoff. The [development checks](COMPETITION_DEVELOPMENT.md) and [56-message diagnostic](INDEPENDENT_RESULTS.md) document the same model and the evidence behind the release decision.

## Publish and submit

1. Run the [README quickstart](../README.md#what-we-built) from the repository root. The verifier prints the 0.35 alert cutoff, the manifest hash beginning `d628e4fe` and `human_reviewed`. In the app, copy the Russian phrase from **School announcement**.
2. From the final worktree, publish the exact commit and print the two links.

~~~powershell
$submissionCommit = (git rev-parse HEAD).Trim()
git push origin "${submissionCommit}:refs/heads/codex/tilswitch-veritas-final"
if ($LASTEXITCODE -ne 0) { throw 'Publication failed.' }
$submissionRepo = 'https://github.com/thorfinn071/TilSwitch-AI-Veritas'
"$submissionRepo/tree/$submissionCommit"
"$submissionRepo/blob/$submissionCommit/README.md"
~~~

3. Open the code and README links without signing in. In the [official form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6), choose **AI + Languages**, use the first link for code and the second as the write-up, and enter entrant details privately. Include the [credits](DATA_AND_MODELS.md). The optional video should be from this checkout and accessible without signing in. Save the submission confirmation and the exact links.
4. The verified public fallback is [988119e](https://github.com/thorfinn071/TilSwitch-AI-Veritas/tree/988119e483ffd6b8c26e9543a98e7ec044e592d0). If using that version, pair it with [its own README](https://github.com/thorfinn071/TilSwitch-AI-Veritas/blob/988119e483ffd6b8c26e9543a98e7ec044e592d0/README.md). The fallback uses the original classifier and its own evaluation.

The organizer accepts a visible code link and one write-up. An optional video can run up to two minutes. Under the organizer's published schedule, the deadline is November 15 at 11:59 p.m. ET, November 16 at 09:59 in Qyzylorda. [Project briefs and submission](https://highschoolhackathon.org/briefs) · [Judging](https://highschoolhackathon.org/judges)

## Video script (1 minute 55 seconds)

| Time | On screen | English narration |
|---|---|---|
| 00:00–00:15 | Open an empty local input. | “A school message can start in Kazakh and give the meeting place in Russian. TilSwitch helps students find the phrase they need help with.” |
| 00:15–00:43 | Paste `Ертең в актовом зале,  сразу после уроков жиналамыз.` Click Analyze, then Copy beside the full Russian phrase. Paste into a blank local editor. | “The Russian phrase includes the place and time. One click copies it, including the comma and both spaces. The classifier runs locally on the CPU.” |
| 00:43–01:01 | Analyze `Бүгін ссылка дайын`, then `Асханаға позже барамыз`. | “In the first message, the underlined word supports a possible switch. The stronger Russian word in the second message supports a firm Mixed result.” |
| 01:01–01:33 | Show the two evaluation rows in the README. | “We extended the starter from sentence labels to copyable spans. On 36 KRCS messages, the script rule scored 0.541 word macro-F1 and our original release scored 0.897. The current release found 15 of 16 mixes in a separate public sample. Two independent human reviews later matched every scoring label.” |
| 01:33–01:55 | Analyze `Он адам зардап шекті.` Show the Russian highlight on `Он`. | “Here, the first word means ‘ten’ in Kazakh. The model guesses Russian and triggers a false alert. Next we want to time how quickly students find the right phrase.” |

The [KRCS and Tatoeba examples](RESULTS.md) carry their original attribution. Prepare the public video from the contest app if attaching one. The older recording shows a different build.

## Five-minute live pitch

| Time | Content |
|---|---|
| 0:00–0:40 | Introduce a student who needs to find the location in a Kazakh–Russian school announcement. Open the local app and ask the judges to look for the Russian phrase. |
| 0:40–1:45 | Paste the mixed message with comma and double space. Analyze, choose the Russian span and paste it back from the clipboard. Show `Бүгін ссылка дайын` and explain the dotted underline. |
| 1:45–2:35 | Describe Tatoeba's sentence-derived training labels, the character patterns and the word-only versus context choice. Explain how the original text offsets and the rule for single-letter words make full phrases copyable. |
| 2:35–3:55 | Show word and message metrics with denominators. Give the original KRCS baseline comparison, the dev comparison between 0.20 and 0.35, and the follow-up human review of the 56-message references. Show both monolingual false-alert counts and the one missed firm alert. |
| 3:55–5:00 | Run the `Он` error, identify the intended reading, and explain why all-context inference lost genuine one-word switches on development. Describe the [student timing pilot](PHRASE_FINDING_PILOT.md). |

### Q&A

- **Can a firm Mixed result be wrong?** Yes. In the public diagnostic, it was wrong on 2 of 17 Kazakh-only and 1 of 7 Russian-only references. The demo shows an omograph that still triggers it.
- **Why 0.35?** A higher margin affects the firm alert supported by a lone word. On the 84 development messages it removed two Russian-only firm alerts compared with 0.20, with all 36 confirmed mixes still detected. The word predictions stayed the same.
- **Who labeled the 56 messages?** The original run used human R1 and an AI worksheet from ChatGPT. In a later blind comparison, human R1 and the replacement human R2 agreed on 383/383 word labels. Their reference matched all 472 scoring rows, and the saved predictions reproduced the reported metrics.
- **What is original?** The challenge starter labels a sentence. We identify word-level changes between languages that share Cyrillic, preserve offsets and make the relevant span copyable. The results and credits identify prior research on this language pair and the loanword boundary.
- **Have students found phrases faster?** The full copy workflow passed browser checks. The timed comparison is ready for participants, with correctness and time recorded for each matched task.
