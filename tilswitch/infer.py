from .features import word_rows
from .model import Model, Policy
from .text import KAZAKH_LETTERS, group_segments, normalize_word, tokenize, validate_text
from .types import LANGUAGES, SCHEMA, Token


def _heuristic(token: Token) -> str:
    if token.script == "latin":
        return "en"
    return "kk" if KAZAKH_LETTERS.intersection(normalize_word(token.text)) else "ru"


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
            script_matches = (label == "en") == (tokens[index].script == "latin")
            reason = None
            if not target_nnz[offset]:
                reason = "unseen_features"
            elif not script_matches:
                reason = "script_mismatch"
            elif scores[top] - scores[runner_up] < policy.threshold:
                reason = "low_margin"
            classified[index] = ("unk" if reason else label, reason)
    predictions = []
    counts = dict.fromkeys((*LANGUAGES, "unk", "neutral"), 0)
    for index, token in enumerate(tokens):
        if not token.lexical:
            label, reason = "neutral", token.reason
        elif token.reason:
            label, reason = "unk", token.reason
        elif model:
            label, reason = classified[index]
        else:
            label, reason = _heuristic(token), None
        counts[label] += 1
        predictions.append({"start": token.start, "end": token.end, "text": token.text,
                            "label": label, "reason": reason})

    active = [label for label in LANGUAGES if counts[label]]
    lexical_count = len(tokens) - counts["neutral"]
    if len(active) >= 2:
        status = "mixed"
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
