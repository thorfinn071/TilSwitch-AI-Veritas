from __future__ import annotations

import platform
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.special import softmax

from .features import feature_matrix, vectorizer
from .types import LANGUAGES, SCHEMA, InputError, file_sha, new_artifact_dir, read_json, write_json

CORE_LIBRARIES = ("numpy", "scipy", "scikit-learn", "regex", "threadpoolctl")


@dataclass(frozen=True)
class Policy:
    threshold: float = 0.0
    mixed_review_recommended: bool = True


@dataclass(frozen=True)
class Model:
    model_id: str
    mode: str
    vocabulary: object
    classes: tuple[str, ...]
    coefficients: np.ndarray
    intercept: np.ndarray
    weight: float
    policy: Policy

    def probabilities(self, rows):
        matrix, target = feature_matrix(rows, self.vocabulary, self.mode, self.weight)
        return softmax(matrix @ self.coefficients.T + self.intercept, axis=1), target.getnnz(axis=1)


def environment_receipt() -> dict:
    return {"python": platform.python_version(), "platform": platform.platform(),
            "libraries": {name: version(name) for name in CORE_LIBRARIES}}


def save_bundle(path: Path, model: Model, metadata: dict):
    with new_artifact_dir(path) as output:
        weights = output / "weights.npz"
        np.savez_compressed(weights, idf=model.vocabulary.idf_, coefficients=model.coefficients,
                            intercept=model.intercept)
        write_json(output / "vocabulary.json", {term: int(index) for term, index in model.vocabulary.vocabulary_.items()})
        write_json(output / "metadata.json", {**metadata, "schema_version": SCHEMA, "model_id": model.model_id,
                                               "mode": model.mode, "classes": model.classes,
                                               "neighbor_weight": model.weight})
        write_json(output / "policy.json", {"threshold": model.policy.threshold,
                                           "mixed_review_recommended": model.policy.mixed_review_recommended})
        write_json(output / "manifest.json", {name: file_sha(output / name) for name in
                                               ("weights.npz", "vocabulary.json", "metadata.json", "policy.json")})


def load_bundle(path: Path, expected_sha: str | None = None) -> Model:
    manifest_path = path / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Model bundle not found at {path}. Point --bundle to a trained release.")
    if expected_sha is not None and file_sha(manifest_path) != expected_sha:
        raise InputError("Model manifest hash differs from the locked hash.")
    manifest = read_json(manifest_path)
    if set(manifest) != {"weights.npz", "vocabulary.json", "metadata.json", "policy.json"}:
        raise InputError("Unexpected model manifest entries.")
    if any(file_sha(path / name) != digest for name, digest in manifest.items()):
        raise InputError("Model bundle checksum mismatch.")
    meta = read_json(path / "metadata.json")
    policy = read_json(path / "policy.json")
    classes = tuple(meta["classes"])
    mode = meta["mode"]
    weight = meta["neighbor_weight"]
    if (meta["schema_version"] != SCHEMA or set(classes) != set(LANGUAGES)
            or len(classes) != len(LANGUAGES) or mode not in {"word", "context"}
            or not 0 <= weight <= 1 or not 0 <= policy["threshold"] <= 1
            or type(policy["mixed_review_recommended"]) is not bool):
        raise InputError("Incompatible model schema, labels or policy.")
    vocabulary = read_json(path / "vocabulary.json")
    size = len(vocabulary)
    if not 0 < size <= 30000 or set(vocabulary.values()) != set(range(size)):
        raise InputError("Invalid TF-IDF vocabulary indices.")
    with np.load(path / "weights.npz", allow_pickle=False) as weights:
        coefficients, intercept, idf = (weights[name] for name in ("coefficients", "intercept", "idf"))
    multiplier = 3 if mode == "context" else 1
    if (coefficients.shape != (len(classes), size * multiplier) or intercept.shape != (len(classes),)
            or idf.shape != (size,) or not all(np.isfinite(array).all() for array in (coefficients, intercept, idf))
            or (idf <= 0).any()):
        raise InputError("Invalid model weight shapes or values.")
    vocab = vectorizer(size, vocabulary=vocabulary)
    vocab.idf_ = idf
    return Model(meta["model_id"], mode, vocab, classes, coefficients, intercept, weight,
                 Policy(policy["threshold"], policy["mixed_review_recommended"]))
