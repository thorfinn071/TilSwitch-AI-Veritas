# Data, model and credits

## Data sources

| Source | Use in this release | License and attribution |
|---|---|---|
| Tatoeba weekly per-language sentence exports and translation links | Sentence-labeled training, development and monolingual test for Kazakh, Russian and English. The inputs were fetched from the Nov 14, 2026 snapshot. | CC BY 2.0 FR for the regular text exports. Credit Tatoeba and the named contributor on any reproduced example. [Tatoeba downloads](https://tatoeba.org/en/downloads) |
| KRCS by Maksim Borisov, Zhanibek Kozhirbayev and Valentin Malykh | One bilingual reviewer labeled 12 screened originals for development and 36 for the held-out test. Spellings are compiled using separate original–translation groups after excluding duplicates of those reviewed groups. Each alignment supplies weak evidence. | Quoted examples, their annotations and the derived `word-evidence.json` in both bundles are shared under CC BY-SA 4.0. [Pinned author release](https://github.com/madrugado/KRCS/tree/9f4fea488bd85490c23ba33ebecc9362d901a21e) · [Paper](https://arxiv.org/abs/2503.20007) · [License](https://creativecommons.org/licenses/by-sa/4.0/) |
| KazNLP by Bogdan Savelyev | The author's validation and test splits provide document labels for the earlier review-policy checks. The 60-message cutoff comparison uses selected texts from the author's training split with AI-drafted, bilingual-confirmed word labels. Logistic regression was fit on Tatoeba. | The release provides aggregate results. Retrieve the original texts from the pinned source. [Author repository](https://github.com/naadgob/KazNLP/tree/f5d5be8108179aded06e145ad6eb019489f207e4/data/training/filter/v1) · [Annotation paper](https://arxiv.org/abs/2608.00581) |
| Kazakh Code-Switch ASR by Timur Seidalin | Three transcript excerpts are in the development side of the local review batch. The 60 messages scored for cutoff selection come from KazNLP. | CC BY 4.0. [Source and attribution](https://huggingface.co/datasets/Tim2190/kazakh-codeswitch-asr) |
| Meta FLORES-200 | Parallel human-translated texts supply paired development and holdout fragments for the word-recovery comparison. The original author split isolates the test groups from development. | CC BY-SA 4.0. [Release and license](https://github.com/facebookresearch/flores) |
| Team-written examples | Demo input and test fixtures. The example text shows expected use without claiming measured performance. | Text written for the project with AI assistance. |

The training cache and review sheets are local. The bundled weights and vectorizer contain character n-grams and coefficients. The release evidence includes aggregate scores, evaluation locks, source receipts and attributed excerpts. Exact KRCS and cutoff reproduction requires the corresponding local annotations.

## Model card

- **Submission bundle** `word-recovery-c128f8d165-switch-486d1f967c` under `release/submission/model`. It uses CPU-only character TF-IDF and multinomial logistic regression, with evidence for informal spellings and contextual support for common single-letter words. The script rule is the original baseline. The context variant adds position-specific features from one word on either side.
- **Training** 2,000 sentences per language. 11,501 Kazakh, 10,243 Russian and 14,066 English eligible target words. Training labels were inherited from source sentences. Cognates, names and borrowing can get imperfect weak labels.
- **Intended use** Inspect a short written message for possible Cyrillic Kazakh, Russian or English spans. Use the language indications to select a phrase for human help or translation.
- **Known errors** Shared words, borrowings and informal spellings can flip a phrase. On the cutoff-selection set, 10 of the 14 indeterminate messages still produced firm alerts. Unsupported Latin text such as `Salem qalaysyn` and `bonjour tout le monde` can be marked English. Isolated letters and unsupported scripts can produce uncertainty.
- **Policy** A score gap of 0.10 governs word labels. A lone word needs a gap of 0.35 to support a firm message alert. The 0.20 reference in `release/model` shares the vocabulary, fitted weights and spelling evidence. [Cutoff comparison](../release/submission/reviewed-switch.json)
- **Persistence** The release contains fitted vocabulary JSON, numeric arrays in NPZ, metadata, policy, a word-evidence lookup and SHA-256 manifests. The inference loader disables pickle and supports the older four-file model bundles. [Results and reproduction](RESULTS.md)

## Tools and prior work

OpenAI Codex assisted with planning, coding, documentation, testing and the first draft of the earlier 60-message comparison labels. [ChatGPT](https://chatgpt.com/) produced the R2 worksheet and participated in the two disputed decisions for the separate 56-message diagnostic. The fitted model was trained for this project with scikit-learn. [Annotation provenance](INDEPENDENT_RESULTS.md)

[Project Briefs, language identification starter](https://highschoolhackathon.org/briefs) · [KazRusCSW prior work](https://github.com/liminovna/KazRusCSW) · [OpenAI Codex](https://openai.com/codex/) · [Python](https://www.python.org/) · [NumPy](https://numpy.org/) · [SciPy](https://scipy.org/) · [scikit-learn](https://scikit-learn.org/) · [regex](https://pypi.org/project/regex/) · [threadpoolctl](https://pypi.org/project/threadpoolctl/) · [Gradio](https://gradio.app/) · [pytest](https://docs.pytest.org/) · [Playwright](https://playwright.dev/python/) · [uv](https://docs.astral.sh/uv/). The dependency locks list transitive packages and exact versions.
