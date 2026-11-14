# TilSwitch AI product specification

## The user and the decision

**Primary persona** A Kazakhstani high-school student who reads one of Kazakh or Russian more fluently than the other and receives a short school message that combines them. The moment of use is deciding which phrase to copy to a translator or ask a friend about. The app reduces the search for that phrase and keeps the decision with the student. Verify the workflow with a teammate or another speaker using invented school messages, with no private chat exports.

| Persona considered | Typical job | MVP fit |
|---|---|---|
| Student in a school or club group chat | Find the unfamiliar phrase in a deadline, timetable or room-change message. | Primary. Short examples, low-risk manual action and a demo judges can follow. |
| Customer-support agent | Route a message to a bilingual queue. | Valuable later. False routing has higher costs and needs representative data and policy. |
| Translation or accessibility tool | Decide which spans to pass to a downstream engine. | Possible integration. Added latency, service and reliability obligations. |
| Researcher or teacher | Inspect switching patterns or build language exercises. | Useful follow-on. Needs larger, well-documented samples and additional workflows. |

## Interaction and page layout

1. Open a single page with the product name, one sentence of scope and a labeled message box. Place two or three example buttons below the field. A button copies its authored example into the box and clears any stale result.
2. Paste a message of at most 1,000 Python Unicode code points. Press **Analyze** using mouse, touch or keyboard. Keep multiline input as typed. Provide a **Clear** control.
3. Show the original text with language highlighting, followed by a small status summary and a numbered segment list in source order. Each row includes the readable language, the text and a review label if needed. A student can select and copy a specific phrase with native text selection. A separate clipboard control is optional.
4. Show **Mixed languages** or **Mixed language evidence · review** according to the locked validation policy. Other status labels are **One language detected**, **Needs review** and **No words to analyze**. Include counts and the detected share of words, with the denominator explained. Show **Review uncertain words before using the result** when unknown word evidence is present. A one-sentence scope note covers Cyrillic Kazakh and Russian, English, and uncertainty on names or romanization.
5. Offer a short expandable explanation for judges with actual model version, counted known and uncertain words and a link to the published evaluation, if available. The page has no language picker, login, translation integration or setup step for a local reviewer.

Use one centered column (max 960 CSS px with 16 px mobile gutters). At 360 px the title, input, buttons, legend, result and segment list stay in one flow without horizontal scroll. At 768 px or wider, example controls align beside each other when they fit. Input and result have enough vertical space for a few short lines. Long words and URLs wrap with CSS and maintain original string content for copying.

| UI state | Behavior |
|---|---|
| Ready | Empty field, examples visible, no fake prediction. |
| Editing | Current typed text stays. Clear the old result on a new example or submission. Mark a prior result as applying to the previous submitted text if the user edits manually and the framework cannot clear it without a round trip. |
| Busy | Show processing near the button. Serialize requests or disable Analyze while a request runs. The latest counter/demo state corresponds to its submitted value. |
| Empty, invalid or over limit | State the problem near the field, retain input, clear prior result and provide a retry. Never silently truncate. |
| Neutral only | Display the original with a plain status and no percentage denominator. |
| Success | Highlight language and uncertain spans, show readable labels and the word counts. Whitespace and punctuation retain their positions. |
| Weak evidence | Keep the original visible. Render unknown spans with a review label. Show unknown coverage without assigning an invented certainty percentage. |
| Model unavailable | Show a recoverable message and local launch/build instructions. The CLI returns a clear error. |
| Clear | Reset input and result. Return the keyboard path to the text area where supported. |

## Visual and accessibility decisions

Use Gradio Blocks with native components. The visual direction comes from the UI/UX Pro Max minimal single-column result, with darker accessible teal and a quieter form. Use **Inter** where locally available, then system UI and a Cyrillic-capable system fallback. Verify Kazakh glyphs in the actual browser. Body 16 px, line height 1.5, heading 28–32 px, controls at least 44 px tall, focus ring 2 px, spacing scale 4/8/12/16/24/32 px, corner radius 8 px. Keep feedback native and motion minimal.

| Role | Foreground | Surface |
|---|---|---|
| Page | #11242B | #F6FAFA |
| Quiet text | #42616C | #FFFFFF |
| Analyze | #FFFFFF | #075E58 |
| Kazakh (KK) | #005047 | #DBF5ED |
| Russian (RU) | #781E37 | #FCE8ED |
| English (EN) | #263F81 | #E7EDFF |
| Neutral | #3C4856 | #EDF0F3 |
| Needs review | #664500 | #FFF1D3 |

The specified text pairs yield at least a 6.65:1 contrast ratio by the luminance formula. Confirm ratios again against the colors actually applied by the framework and check focus states on white and tinted surfaces. Text segment rows and their language names communicate the same information as the highlights. Add meaningful form labels, a logical focus order, a status update readable by assistive tech and zoom reflow. Check 200% zoom and reduced motion. Neutral punctuation, emoji and whitespace stay visually plain. Use actual result segments to build Gradio HighlightedText from raw substrings and label categories. Pass gap strings with an empty category. For a fallback display, show original plain text and a labeled segment table. [Gradio HighlightedText](https://www.gradio.app/docs/gradio/highlightedtext)

The implemented renderer uses escaped HTML in Gradio Blocks so the original message, its highlighting, and the labeled phrase list use the same inference offsets. A browser test verifies copied text content and rejects interpreted user markup. The detail panel shows the model ID and what the counts cover.

## MVP acceptance and demo

- A user can complete one paste → analyze → identify phrase → select/copy loop without instructions beyond the form. Record a brief task check with an invented school-chat example. If solo, record a self-check and identify its limitation.
- Run one monolingual example, the supplied Kazakh–Russian sample, a real allowed and sanitized held-out prediction/reference comparison, and an ambiguous short example. Use the published model for every shown prediction.
- Support exploratory English spans with the same output format. Demo Russian–English and triple mixes as behavior checks unless the actual slices have enough reviewed examples for a quantitative claim.
- A neutral-only message shows no language claim. An unsupported script or mixed-script word falls to review. An unsupported Latin or Cyrillic language can be mislabeled by a closed-set model. Keep the scope note visible.
- When no model is available, no statistics or highlighting are rendered. The UI remains usable at 360 px and with keyboard alone. Assess against the [QA cases](TESTING_PLAN.md#user-acceptance).
- Optional improvements after the first working release are a quick-copy action, bilingual labels and an accessible coverage graphic. Team translation, auto-routing to other people's inboxes, file uploads, login, telemetry and saved message history are outside the MVP.

## Privacy behavior

Default to localhost with Gradio sharing off, analytics off and no text logging or persistence. The demo, tests and video use team-authored samples or text approved for display after dataset and privacy review. An optional hosted version would send pasted text to a server and must carry an accurate disclosure before use. [Runtime contract](ARCHITECTURE.md) · [Gold data policy](ML_RESEARCH_PLAN.md)
