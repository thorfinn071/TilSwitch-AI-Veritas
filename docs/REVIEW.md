# Blind Kazakh–Russian review

Use the local `data/review/krcs-dev.tsv` and `data/review/krcs-test.tsv` sheets. They contain 12 development messages and 36 held-out messages, respectively. These are published corpus samples and should stay in the local workspace during review. Keep the test sheet free of model predictions.

1. Review the whole message in the `text` column, then label the word or symbol in `surface`. Repeated message text groups the word rows visually. The `message_id` and `token_index` identify each row.
2. Fill `label` with `kk`, `ru`, `en`, `neutral`, `ambiguous`, `other` or `unknown`. Leave existing neutral punctuation, links, numbers and emoji as labeled. Mark clear proper names neutral. Mark integrated borrowings in the receiving language where current use is clear.
3. For `ambiguous`, `other` or `unknown`, give a short reason such as `shared`, `hybrid`, `romanized_kk` or `cannot_identify`. Use your reviewer code, for example `R1`, in `reviewer` for every row whose label was blank.
4. In the Excel copies, edit `label`, `reason` and `reviewer`. Merge those columns into the local TSV by `message_id` and `token_index` after verifying the original fields. If editing the TSV directly, keep the fixed columns and UTF-8 tab separation. If a message contains identifying information that should be dropped, record its message ID separately.
5. Validate the development sheet first. Resolve guideline questions before applying the same policy to held-out labels. Use the same validation command with `--split test` for the final sheet.

~~~powershell
& .\.venv\Scripts\python.exe -m tilswitch review validate --dataset krcs --split dev
& .\.venv\Scripts\python.exe -m tilswitch review validate --dataset krcs --split test
~~~

See the [labeling policy](ML_RESEARCH_PLAN.md#annotation-guideline-v1) for names, borrowing and ambiguity. Record how many fluent reviewers participated and what each covered. If another bilingual reviewer is available, let them label 12 test messages independently using a separate copy. Record both independent outputs and report the agreement and adjudication process before finalizing the main sheet. A second pass by the same person can be reported as a consistency check.

After both sheets pass validation, lock the external run and then score the holdout. Before scoring, check the lock for `informal_dev`, the selected model, thresholds and `test.krcs.supports_primary`. The [research plan](ML_RESEARCH_PLAN.md#targets-split-and-deduplication) requires at least 12 reviewed development messages and four messages per reference language for KRCS-based selection. The primary test claim requires 36 reviewed messages, at least 12 short messages and at least 30 scorable words from eight or more messages per Kazakh and Russian label. Report descriptive results for slices with insufficient support. Keep the monolingual run as a separate result. Use fresh output paths for replays.

~~~powershell
& .\.venv\Scripts\python.exe -m tilswitch lock --datasets krcs --out artifacts/runs/krcs-v1.lock.json
& .\.venv\Scripts\python.exe -m tilswitch evaluate --phase test --lock artifacts/runs/krcs-v1.lock.json --out artifacts/runs/krcs-v1
& .\.venv\Scripts\python.exe -m tilswitch release --lock artifacts/runs/krcs-v1.lock.json --out artifacts/models/krcs-release
~~~

Review the resulting evidence and check the candidate with `python -m tilswitch demo --bundle artifacts/models/krcs-release` before replacing the submission’s default release. Both splits of the published run were labeled by one bilingual reviewer. [Locked results](RESULTS.md#locked-krcs-evaluation-nov-15-2026)
