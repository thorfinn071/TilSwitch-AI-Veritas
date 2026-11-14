import heapq
from dataclasses import dataclass

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

from .text import neighbors, normalize_word, tokenize
from .types import LANGUAGES, RunConfig, Token, stable_key


@dataclass(frozen=True)
class WordRow:
    surface: str
    previous: str = ""
    following: str = ""


def word_rows(raw: str, tokens: list[Token], with_context: bool):
    context = neighbors(raw, tokens) if with_context else None
    for index, token in enumerate(tokens):
        if token.lexical and token.reason is None:
            previous, following = context[index] if context is not None else ("", "")
            yield index, WordRow(normalize_word(token.text), previous, following)


def training_words(messages, cfg: RunConfig):
    groups = {label: [] for label in LANGUAGES}
    for message in messages:
        text = message["text"]
        tokens = tokenize(text)
        label = message["source_lang"]
        for index, row in word_rows(text, tokens, with_context=True):
            key = f'{message["message_id"]}:{tokens[index].start}'
            groups[label].append((stable_key(cfg.split_seed, key), key, row))
    items = []
    for label in LANGUAGES:
        chosen = heapq.nsmallest(cfg.train_tokens_per_language, groups[label], key=lambda x: x[:2])
        items.extend((label, row) for _, _, row in chosen)
    return items


def vectorizer(max_features: int, vocabulary=None):
    return TfidfVectorizer(analyzer="char", ngram_range=(1, 4), min_df=2, max_features=max_features,
                           sublinear_tf=True, lowercase=False, vocabulary=vocabulary)


def marked(word: str) -> str:
    return f"^{word}$" if word else ""


def feature_matrix(rows: list[WordRow], vocab: TfidfVectorizer, mode: str, weight: float):
    target = vocab.transform([marked(row.surface) for row in rows])
    if mode == "word":
        return target, target
    previous = vocab.transform([marked(row.previous) for row in rows])
    following = vocab.transform([marked(row.following) for row in rows])
    return hstack((target, previous * weight, following * weight), format="csr"), target
