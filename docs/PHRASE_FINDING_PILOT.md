# TilSwitch phrase-finding pilot

Can students find the exact Russian or Kazakh phrase in a mixed school announcement more quickly with TilSwitch highlights? A facilitator can run the session in about ten minutes per participant with six to eight consenting students. Use the permission process that applies to participants. Keep the tasks synthetic and record no names, messages from participants, or contact details. Eight participants let each presentation sequence run twice. There have been zero participant sessions.

## Procedure

1. Prepare a plain card and a highlighted card for each message below. Use the judging build with `release/submission/model` to render the highlighted spans, including any errors or uncertain colors. Use the same screen, font, line breaks, font size, and standard text selection and copy controls in both conditions. Keep the highlight legend visible in the highlighted condition. Keep the message status and one-click phrase-copy button off both displays to isolate the visual cue.
2. Give one practice message outside the task deck. Tell participants they will see an announcement and the name of the target language. They should copy the full span in that language into an answer field. The facilitator keeps the target span hidden. Keep the task instruction, timing and answer interaction identical for both conditions.
3. Assign anonymous participant codes and cycle through the four sequences below. Each participant sees each item once. Use the numbered task order in each block. Reveal the prompt and message together, start timing on reveal and stop on answer submission or after 45 seconds. Give no hints or accuracy feedback until the session ends.
4. Save the answer text from the synthetic stimulus only, the elapsed seconds, whether the answer exactly matched the full span after trimming outer whitespace, and whether it timed out. Retain wrong answers and timeouts in the totals. Ask optionally what made a phrase easy or hard to find and record a short anonymous paraphrase.

| Sequence | First block | Second block |
| --- | --- | --- |
| 1 | A plain | B highlighted |
| 2 | A highlighted | B plain |
| 3 | B plain | A highlighted |
| 4 | B highlighted | A plain |

## Matched tasks and facilitator key

Each pair matches target language, phrase length, approximate position and type of announcement. Put just the language prompt and message on the participant card.

| Task | Message | Prompt language | Exact target |
| --- | --- | --- | --- |
| A1 | Кездесу бүгін төртте, после последнего урока аудиторияға жиналайық. | Russian | после последнего урока |
| B1 | Көрме ертең ашылады, перед первым уроком дәлізге жиналайық. | Russian | перед первым уроком |
| A2 | Пожалуйста, отправьте жұмыс кестесін утром в общий чат. | Kazakh | жұмыс кестесін |
| B2 | Сначала проверьте сынып тізімін вместе с куратором. | Kazakh | сынып тізімін |
| A3 | Жаттығуды аяқтаған соң, позвони. | Russian | позвони |
| B3 | Кітапты орнына қойсаң, напиши. | Russian | напиши |
| A4 | Зал откроют ровно в шесть, асықпа. | Kazakh | асықпа |
| B4 | Двери закроют ровно в семь, кешікпе. | Kazakh | кешікпе |

## Recording and analysis

Copy this template and use one row per task. Optionally record broad self-described language comfort, with a skip option. Fix the tasks and success criteria before anyone sees them. Verify that the displays show the assigned stimuli, and record any model highlighting errors before the session.

| Participant code | Sequence | Task | Plain or highlighted | Pasted answer | Seconds | Exact | Timeout | Note |
| --- | ---: | --- | --- | --- | ---: | --- | --- | --- |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

Report the number of participants, completions, correct spans and timeouts per condition. For each participant, calculate the median time for the correct answers in each condition and report the median paired difference across participants with a valid time in both conditions. Give that participant count and report each condition's completion ratios beside the time result. For an all-task summary, assign incorrect answers and timeouts the 45-second cap and report the paired median difference under that convention as well. Tabulate any case where highlighting consistently leads to an incorrect selection.

A small pilot can show whether the task and interface are usable and surface problems to fix. A larger sample and realistic, permissioned material would be needed to estimate time savings across students or actual chats.

The preparation check found all eight target spans in the 0.35 output. The deck therefore tests phrase-finding when the model supplies a usable highlight. The blind annotation study tests how often the model supplies correct highlights.
