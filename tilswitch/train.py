from collections import Counter
from pathlib import Path
from time import perf_counter
import warnings

from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits

from .augment import informal_words
from .features import feature_matrix, marked, training_words, vectorizer
from .model import Model, Policy, environment_receipt, save_bundle
from .prepare import verified_split
from .types import LANGUAGES, InputError, RunConfig, file_sha, read_rows, text_sha


def fit_model(messages, cfg: RunConfig, mode: str, train_sha: str, *, informal: bool = False) -> tuple[Model, dict]:
    if informal and mode != "word":
        raise InputError("Informal augmentation supports the word model.")
    started = perf_counter()
    words = training_words(messages, cfg)
    counts = Counter(label for label, _ in words)
    if set(counts) != set(LANGUAGES):
        raise InputError("Training requires words from every supported language.")
    model_id = f"{mode}-{train_sha[:10]}"
    augmentation = {}
    if informal:
        budget = min(2_000, cfg.train_tokens_per_language - counts["kk"])
        if budget <= 0:
            raise InputError("No informal variants fit the configured training word limit.")
        additions, receipt = informal_words(words, cfg.split_seed, budget)
        if not additions:
            raise InputError("No distinct informal variants could be generated.")
        words.extend(additions)
        counts["kk"] += len(additions)
        model_id = "word-informal-" + text_sha(train_sha + receipt["sha256"])[:10]
        augmentation = {"informal_augmentation": receipt}
    labels, rows = zip(*words)
    vocab = vectorizer(cfg.max_features)
    matrix, _ = feature_matrix(list(rows), vocab.fit([marked(row.surface) for row in rows]),
                               mode, cfg.neighbor_weight)
    with threadpool_limits(limits=1):
        for iterations in (400, 800):
            estimator = LogisticRegression(C=1.0, solver="lbfgs", class_weight="balanced",
                                           max_iter=iterations, random_state=cfg.split_seed)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                estimator.fit(matrix, labels)
            converged = all(not issubclass(warning.category, ConvergenceWarning) for warning in caught)
            if converged:
                break
        else:
            raise InputError(f"The {mode} model reached its iteration limit twice.")
    model = Model(model_id, mode, vocab, tuple(estimator.classes_),
                  estimator.coef_, estimator.intercept_, cfg.neighbor_weight, Policy())
    metadata = {"train_sha256": train_sha, "training_word_counts": dict(counts),
                "features": matrix.shape[1], "vocabulary_size": len(vocab.vocabulary_),
                "fit_seconds": round(perf_counter() - started, 3), "iterations": int(estimator.n_iter_.max()),
                "max_iterations": iterations, "split_seed": cfg.split_seed, "environment": environment_receipt(),
                **augmentation}
    return model, metadata


def train(cfg: RunConfig, mode: str, *, informal: bool = False) -> tuple[Path, dict]:
    source_path = verified_split(cfg, "train")
    model, metadata = fit_model(read_rows(source_path), cfg, mode, file_sha(source_path), informal=informal)
    bundle_path = cfg.models / ("word-informal" if informal else mode)
    save_bundle(bundle_path, model, metadata)
    return bundle_path, metadata
