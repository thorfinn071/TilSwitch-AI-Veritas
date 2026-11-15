from .features import WordRow
from .text import VOICELESS, kazakh_instrumental
from .types import stable_key, text_sha


INFORMAL_LETTERS = str.maketrans("әғқңөұүһі", "агкноуухи")

# The groups supply back and front vowel harmony for common loan nouns.
LOAN_NOUNS = (
    ("а", "ғ", "қ", (
        "автобус", "альбом", "анкета", "гардероб", "грант", "диктофон",
        "журнал", "компас", "лаборант", "ламинат", "макарон", "микрофон",
        "монитор", "мотор", "плакат",
        "протокол", "рюкзак", "сайт", "салон", "стадион", "тариф",
        "формат", "чат", "штатив", "экран",
    )),
    ("е", "г", "к", (
        "адаптер", "билет", "браузер", "график", "кабель", "конверт",
        "курьер", "маркер", "наушник", "пакет", "пароль", "пластик",
        "принтер", "проект", "регламент",
        "режим", "рецепт", "сервер", "степлер", "стенд", "свитер",
        "текст", "трек", "турникет", "чек", "штекер",
    )),
)


def loan_forms():
    for vowel, voiced_dative, voiceless_dative, nouns in LOAN_NOUNS:
        for noun in nouns:
            final = noun.rstrip("ь")[-1]
            dative = voiceless_dative if final in VOICELESS else voiced_dative
            locative = "т" if final in VOICELESS else "д"
            yield noun + dative + vowel
            yield noun + locative + vowel
            yield noun + kazakh_instrumental(final)


def informal_words(words, seed: int, limit: int):
    """Make distinct Kazakh variants from training words and scripted loan forms."""
    occupied = {row.surface for _, row in words}
    loans = set(loan_forms()) - occupied
    folded = {row.surface.translate(INFORMAL_LETTERS) for label, row in words if label == "kk"} - occupied - loans

    def take(items, count):
        return sorted(items, key=lambda text: (stable_key(seed, text), text))[:count]

    borrowed = take(loans, limit // 4)
    respelled = take(folded, limit - len(borrowed))
    surfaces = borrowed + respelled
    receipt = {"borrowed_forms": len(borrowed), "informal_spellings": len(respelled),
               "sha256": text_sha("\n".join(surfaces))}
    return [("kk", WordRow(text)) for text in surfaces], receipt
