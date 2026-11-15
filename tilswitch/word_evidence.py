from dataclasses import dataclass

from .text import context_indices, normalize_word
from .types import InputError


EVIDENCE_MARGIN = 0.50
RUSSIAN_PREPOSITIONS = frozenset("вкосу")
RUSSIAN_FUNCTION_WORDS = frozenset("аия")


@dataclass(frozen=True)
class WordEvidence:
    kazakh_spellings: frozenset[str]
    parallel_spellings: frozenset[str]

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict) or set(data) != {"kazakh_spellings", "parallel_spellings"}:
            raise InputError("Unexpected word-evidence fields.")
        lists = (data["kazakh_spellings"], data["parallel_spellings"])
        if any(not isinstance(items, list) or len(items) > 30_000
               or any(not isinstance(word, str) or not 2 <= len(word) <= 1000
                      or word != normalize_word(word) for word in items) for items in lists):
            raise InputError("Invalid word-evidence spellings.")
        local, parallel = (frozenset(items) for items in lists)
        if len(local) != len(lists[0]) or len(parallel) != len(lists[1]) or not parallel <= local:
            raise InputError("Word-evidence spellings must be unique, with parallel spellings in the main list.")
        return cls(local, parallel)

    def to_json(self):
        return {"kazakh_spellings": sorted(self.kazakh_spellings), "parallel_spellings": sorted(self.parallel_spellings)}


def _has_evidence(classified, index, language):
    guess = classified.get(index)
    return guess is not None and guess[0] == language and guess[2] >= EVIDENCE_MARGIN


def _short_word_language(token, left, right, classified):
    word = normalize_word(token.text)
    if word in RUSSIAN_PREPOSITIONS or word in RUSSIAN_FUNCTION_WORDS:
        if left is not None and token.text.isupper():
            return None
        if _has_evidence(classified, right, "ru"):
            return "ru"
        if word in RUSSIAN_FUNCTION_WORDS and _has_evidence(classified, left, "ru"):
            return "ru"
    if word in {"a", "i"} and _has_evidence(classified, right, "en"):
        if word == "i" or left is None or token.text.islower():
            return "en"
    return None


def apply_word_evidence(raw, tokens, candidates, classified, evidence: WordEvidence):
    if evidence.kazakh_spellings:
        neighbors = context_indices(raw, tokens)
        spelling_updates = {}
        for index, row in candidates:
            if (tokens[index].script != "cyrillic" or classified[index][0] == "kk"
                    or row.surface not in evidence.kazakh_spellings):
                continue
            if (row.surface in evidence.parallel_spellings
                    or any(_has_evidence(classified, near, "kk") for near in neighbors[index])):
                spelling_updates[index] = ("kk", None, EVIDENCE_MARGIN)
        classified.update(spelling_updates)

    if not any(token.reason == "short_word" for token in tokens):
        return
    short_updates = {}
    for index, (left, right) in enumerate(context_indices(raw, tokens, include_short=True)):
        token = tokens[index]
        if token.reason == "short_word":
            label = _short_word_language(token, left, right, classified)
            if label is not None:
                short_updates[index] = (label, None, EVIDENCE_MARGIN)
    classified.update(short_updates)
