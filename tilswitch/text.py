import unicodedata

import regex

from .types import InputError, Token

KAZAKH_LETTERS = frozenset("әғқңөұүһі")
APOSTROPHES = "'’ʼ‘"
DASHES = "-‐‑‒–—"
FEATURE_TRANSLATION = str.maketrans({**dict.fromkeys(APOSTROPHES, "'"), **dict.fromkeys(DASHES, "-")})
TERMINAL = frozenset(".!?…")
WORD_PART = r"(?:[\p{L}\p{Nd}]\p{M}*)"
CONNECTOR = regex.escape(APOSTROPHES + DASHES)
SCANNER = regex.compile(
    r"(?P<space>\s+)"
    r"|(?P<link>(?i:https?://|www\.)[^\s<>]+|[\w.+-]+@[\w.-]+\.[\p{L}]{2,})"
    r"|(?P<handle>[@#][\p{L}\p{M}\p{Nd}_]+)"
    r"|(?P<emoji>[#*0-9]\uFE0F?\u20E3|(?=\p{Extended_Pictographic}|\p{Regional_Indicator})\X)"
    r"|(?P<number>\p{Nd}+(?:[.,:/]\p{Nd}+)*(?![\p{L}\p{M}\p{Nd}]))"
    rf"|(?P<word>{WORD_PART}+(?:[{CONNECTOR}](?<=\p{{L}}[{CONNECTOR}])(?=\p{{L}}){WORD_PART}+)*)"
    r"|(?P<grapheme>\X)"
)
LATIN = regex.compile(r"\A\p{Script=Latin}\Z")
CYRILLIC = regex.compile(r"\A\p{Script=Cyrillic}\Z")
LINE_BREAK = regex.compile(r"[\r\n\v\f\x85\u2028\u2029]")
INVALID_CONTROL = regex.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_word(surface: str) -> str:
    surface = unicodedata.normalize("NFC", surface).casefold().translate(FEATURE_TRANSLATION)
    return unicodedata.normalize("NFC", surface)


def validate_text(raw: str) -> None:
    if not isinstance(raw, str) or not raw.strip():
        raise InputError("Enter a message to analyze.")
    if len(raw) > 1000:
        raise InputError("Use at most 1,000 characters.")
    try:
        raw.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        raise InputError("The message contains invalid Unicode.") from None
    if INVALID_CONTROL.search(raw):
        raise InputError("Remove nonprinting control characters from the message.")


def _word(start: int, end: int, surface: str) -> Token:
    normalized = normalize_word(surface)
    letters = [character for character in normalized if character.isalpha()]
    if not letters:
        return Token(start, end, surface, "neutral", reason="number")
    if any(character.isdecimal() for character in normalized):
        return Token(start, end, surface, "word", reason="alphanumeric")
    if all(CYRILLIC.fullmatch(character) for character in letters):
        script = "cyrillic"
    elif all(LATIN.fullmatch(character) for character in letters):
        script = "latin"
    else:
        return Token(start, end, surface, "word", reason="unsupported_or_mixed_script")
    reason = "short_word" if len(letters) < 2 else None
    return Token(start, end, surface, "word", script, reason)


def _trailing_link_punctuation(surface: str) -> str:
    stripped = surface.rstrip(".,!?;:…'\"”’»")
    while stripped.endswith((")", "]", "}")):
        close = stripped[-1]
        open_char = {")": "(", "]": "[", "}": "{"}[close]
        if stripped.count(close) <= stripped.count(open_char):
            break
        stripped = stripped[:-1].rstrip(".,!?;:…")
    return stripped


def tokenize(raw: str) -> list[Token]:
    tokens = []
    for match in SCANNER.finditer(raw):
        kind = match.lastgroup
        start, end = match.span()
        surface = match[0]
        if kind == "space":
            continue
        if kind == "word":
            tokens.append(_word(start, end, surface))
        elif kind == "link":
            link = _trailing_link_punctuation(surface)
            split = start + len(link)
            tokens.append(Token(start, split, link, "neutral", reason="link"))
            for index, character in enumerate(surface[len(link):], split):
                tokens.append(Token(index, index + 1, character, "neutral", reason="punctuation"))
        else:
            reason = "punctuation" if kind == "grapheme" else kind
            tokens.append(Token(start, end, surface, "neutral", reason=reason))
    return tokens


def _ends_context(token: Token) -> bool:
    if token.lexical:
        return token.reason is not None
    return token.reason in {"link", "handle", "number", "emoji"} or bool(TERMINAL.intersection(token.text))


def context_indices(raw: str, tokens: list[Token]) -> list[tuple[int | None, int | None]]:
    left = [None] * len(tokens)
    right = [None] * len(tokens)
    previous = None
    offset = 0
    for index, token in enumerate(tokens):
        if LINE_BREAK.search(raw[offset:token.start]) or _ends_context(token):
            previous = None
        if token.lexical and token.reason is None:
            left[index] = previous
            if previous is not None:
                right[previous] = index
            previous = index
        offset = token.end
    return list(zip(left, right))


def neighbors(raw: str, tokens: list[Token]) -> list[tuple[str, str]]:
    words = {index: normalize_word(token.text)
             for index, token in enumerate(tokens) if token.lexical and token.reason is None}
    return [(words.get(left, ""), words.get(right, "")) for left, right in context_indices(raw, tokens)]


def group_segments(raw: str, predictions: list[dict]) -> list[dict]:
    segments = []
    preceding_lexical = False
    for prediction in predictions:
        label = prediction["label"]
        if label == "neutral":
            preceding_lexical = False
            continue
        start, end = prediction["start"], prediction["end"]
        if preceding_lexical and segments[-1]["label"] == label:
            gap = raw[segments[-1]["end"]:start]
            if gap and all(character in " \t\u00a0\u202f" for character in gap):
                segments[-1]["end"] = end
                segments[-1]["text"] = raw[segments[-1]["start"]:end]
                continue
        segments.append({"start": start, "end": end, "text": raw[start:end], "label": label})
        preceding_lexical = True
    return segments
