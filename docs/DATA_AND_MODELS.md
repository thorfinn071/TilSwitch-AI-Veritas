# Data, model and credits

## Data sources

| Source | Use in this release | License and attribution |
|---|---|---|
| Tatoeba weekly per-language sentence exports and translation links | Sentence-labeled training, development and monolingual test for Kazakh, Russian and English. The inputs were fetched from the Nov 14, 2026 snapshot. | CC BY 2.0 FR for the regular text exports. Credit Tatoeba and the named contributor on any reproduced example. [Tatoeba downloads](https://tatoeba.org/en/downloads) |
| KRCS by Maksim Borisov, Zhanibek Kozhirbayev and Valentin Malykh | 48 screened originals in the local annotation inventory. All accessible originals and translations were compared for overlap against the Tatoeba candidate pool. No KRCS gold scores were used for this release. | CC BY-SA 4.0 at author revision `9f4fea488bd85490c23ba33ebecc9362d901a21e`. Keep derived public annotation materials aligned with source attribution and sharing terms. [Author release](https://github.com/madrugado/KRCS/tree/9f4fea488bd85490c23ba33ebecc9362d901a21e) · [Paper](https://arxiv.org/abs/2503.20007) |
| Meta FLORES-200 | Optional monolingual fallback implemented in the loader. It supplies no rows to the published model. | CC BY-SA 4.0. [Release and license](https://github.com/facebookresearch/flores) |
| Team-written examples | Demo input and test fixtures. The example text shows expected use without claiming measured performance. | Text written for the project with AI assistance. |

The training cache and review sheets are local. The bundled weights and vectorizer contain character fragments and coefficients. Raw source messages, contributor fields and review sheets are excluded from Git by default. The example in the write-up is attributed individually.

## Model card

- **Release** `word-abf81e3da4`, CPU-only character TF-IDF plus multinomial logistic regression. The baseline is a script/letter rule. The context candidate adds position-specific features from one surrounding word on either side.
- **Training** 2,000 sentences per language. 11,501 Kazakh, 10,243 Russian and 14,066 English eligible target words. Training labels were inherited from source sentences. Cognates, names and borrowing can get imperfect weak labels.
- **Intended use** Inspect a short written message for possible Cyrillic Kazakh, Russian or English spans. Use the language indications to select a phrase for human help or translation.
- **Known errors** Closely related or shared words can flip a phrase. A Latin-script language outside the label set can be marked English. Public test evidence concerns the Tatoeba register. A word with a one-letter spelling or an unsupported script is passed to review by explicit rules.
- **Policy** Mixed displays with review wording. The numerical margin threshold is 0 until independent labeled development data is available. The product displays counts and uncertainty reasons.
- **Persistence** The release contains fitted vocabulary JSON, numeric arrays in NPZ, metadata, policy and SHA-256 manifests. The inference loader disables pickle. See [results](RESULTS.md).

## Tools and prior work

[Project Briefs, language identification starter](https://highschoolhackathon.org/briefs) · [KazRusCSW prior work](https://github.com/liminovna/KazRusCSW) · [OpenAI Codex](https://openai.com/codex/) · [Python](https://www.python.org/) · [NumPy](https://numpy.org/) · [SciPy](https://scipy.org/) · [scikit-learn](https://scikit-learn.org/) · [regex](https://pypi.org/project/regex/) · [threadpoolctl](https://pypi.org/project/threadpoolctl/) · [Gradio](https://gradio.app/) · [pytest](https://docs.pytest.org/) · [Playwright](https://playwright.dev/python/) · [uv](https://docs.astral.sh/uv/). The dependency locks list transitive packages and exact versions.
