from .features import WordRow, word_rows
from .model import Model, Policy
from .text import (
    KAZAKH_LETTERS, context_indices, group_segments, kazakh_instrumental, normalize_word, tokenize, validate_text,
)
from .types import LANGUAGES, SCHEMA, Token
from .word_evidence import apply_word_evidence


INSTRUMENTAL_ENDINGS = ("мен", "бен", "пен")
BORROWING_EVIDENCE_MARGIN = 0.50


def _heuristic(token: Token) -> str:
    if token.script == "latin":
        return "en"
    return "kk" if KAZAKH_LETTERS.intersection(normalize_word(token.text)) else "ru"


def _review_borrowings(raw, tokens, candidates, classified, model):
    """Flag a Russian-looking word whose instrumental ending and context suggest Kazakh."""
    neighbors = context_indices(raw, tokens)
    stems = []
    for index, row in candidates:
        if classified[index][0] != "ru" or not row.surface.endswith(INSTRUMENTAL_ENDINGS):
            continue
        stem = row.surface[:-3]
        base = stem.rstrip("ь")
        if len(base) < 3 or not stem.isalpha() or KAZAKH_LETTERS.intersection(stem):
            continue
        if row.surface[-3:] != kazakh_instrumental(base[-1]):
            continue
        nearby = [classified[neighbor] for neighbor in neighbors[index] if neighbor is not None]
        if any(label == "ru" for label, _, _ in nearby):
            continue
        if any(label == "kk" and margin >= BORROWING_EVIDENCE_MARGIN for label, _, margin in nearby):
            stems.append((index, WordRow(stem)))
    if not stems:
        return

    probabilities, seen = model.probabilities([row for _, row in stems])
    russian = model.classes.index("ru")
    for (index, _), scores, features in zip(stems, probabilities, seen):
        next_best = max(score for offset, score in enumerate(scores) if offset != russian)
        stem_margin = scores[russian] - next_best
        word_margin = classified[index][2]
        if features and stem_margin >= BORROWING_EVIDENCE_MARGIN and stem_margin > word_margin:
            classified[index] = ("unk", "kazakh_ending", word_margin)


def analyze(raw: str, model: Model | None, policy: Policy | None = None) -> dict:
    validate_text(raw)
    tokens = tokenize(raw)
    policy = policy or (model.policy if model else Policy())
    candidates = list(word_rows(raw, tokens, with_context=bool(model and model.mode == "context")))
    classified = {}
    if model and candidates:
        probabilities, target_nnz = model.probabilities([row for _, row in candidates])
        for offset, ((index, _), scores) in enumerate(zip(candidates, probabilities)):
            top, runner_up, *_ = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
            label = model.classes[top]
            margin = scores[top] - scores[runner_up]
            script_matches = (label == "en") == (tokens[index].script == "latin")
            reason = None
            if not target_nnz[offset]:
                reason = "unseen_features"
            elif not script_matches:
                reason = "script_mismatch"
            elif margin < policy.threshold:
                reason = "low_margin"
            classified[index] = ("unk" if reason else label, reason, margin)
        if policy.review_kazakh_borrowings and model.mode == "word":
            _review_borrowings(raw, tokens, candidates, classified, model)
        word_evidence = getattr(model, "word_evidence", None)
        if word_evidence is not None:
            apply_word_evidence(raw, tokens, candidates, classified, word_evidence)
    strong_evidence = {
        label for label, reason, margin in classified.values()
        if reason is None and margin >= policy.singleton_switch_margin
    }
    predictions = []
    counts = dict.fromkeys((*LANGUAGES, "unk", "neutral"), 0)
    for index, token in enumerate(tokens):
        if not token.lexical:
            label, reason = "neutral", token.reason
        elif token.reason and index not in classified:
            label, reason = "unk", token.reason
        elif model:
            label, reason, _ = classified[index]
        else:
            label, reason = _heuristic(token), None
        counts[label] += 1
        predictions.append({"start": token.start, "end": token.end, "text": token.text,
                            "label": label, "reason": reason})

    active = [label for label in LANGUAGES if counts[label]]
    lexical_count = len(tokens) - counts["neutral"]
    if len(active) >= 2:
        status = "mixed"
        if model and policy.singleton_switch_margin:
            supported = sum(counts[label] >= 2 or label in strong_evidence for label in active)
            if supported < 2:
                status = "possible_switch"
    elif not lexical_count:
        status = "neutral_only"
    elif counts["unk"]:
        status = "needs_review"
    else:
        status = "single"
    shares = ({label: counts[label] / lexical_count for label in (*LANGUAGES, "unk")} if lexical_count else None)
    return {"schema_version": SCHEMA, "model_id": model.model_id if model else "script-heuristic",
            "offset_unit": "unicode_code_point", "text": raw, "tokens": predictions,
            "segments": group_segments(raw, predictions), "counts": counts, "lexical_count": lexical_count,
            "shares": shares, "status": status, "primary_language": active[0] if status == "single" else None,
            "has_unknown": bool(counts["unk"]), "mixed_review_recommended": policy.mixed_review_recommended}
