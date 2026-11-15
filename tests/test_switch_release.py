from dataclasses import asdict, replace
from pathlib import Path
from shutil import copytree

import pytest

from experiments import package_reviewed_switch
from experiments.verify_submission import verify_submission
from tilswitch.model import load_bundle
from tilswitch.types import InputError, file_sha, read_json, write_json


@pytest.fixture
def locked_comparison(tmp_path, monkeypatch):
    baseline_path = Path("release/model").resolve()
    baseline = load_bundle(baseline_path)
    candidate_policy = replace(baseline.policy, singleton_switch_margin=0.35)
    lock = tmp_path / "lock.json"
    write_json(lock, {"inputs": {
        "bundle": str(baseline_path),
        "bundle_manifest_sha256": file_sha(baseline_path / "manifest.json"),
        "annotations_sha256": "fixture",
        "policies": {"baseline": asdict(baseline.policy), "candidate": asdict(candidate_policy)},
    }})
    metrics = {"lock_sha256": file_sha(lock), "candidate_passed": True}

    def replay(folder):
        assert (folder / "lock.json").read_bytes() == lock.read_bytes()
        write_json(folder / "score" / "metrics.json", metrics)

    monkeypatch.setattr(package_reviewed_switch, "score", replay)
    return lock, baseline_path, candidate_policy, metrics


def test_package_binds_the_tested_policy_and_preserves_word_assets(tmp_path, locked_comparison):
    lock, baseline, policy, metrics = locked_comparison
    output = tmp_path / "candidate"
    result = package_reviewed_switch.package_candidate(lock, output)
    bundle = output / "model"
    assert load_bundle(bundle, result["manifest_sha256"]).policy == policy
    for name in ("weights.npz", "vocabulary.json", "word-evidence.json"):
        assert file_sha(bundle / name) == file_sha(baseline / name)
    evidence = read_json(output / "reviewed-switch.json")
    assert evidence["results"] == metrics
    assert evidence["candidate_model_id"] == load_bundle(bundle).model_id
    assert evidence["candidate_manifest_sha256"] == result["manifest_sha256"]
    assert evidence["provenance"] == read_json(bundle / "metadata.json")["switch_comparison"]
    assert read_json(lock)["inputs"]["bundle_manifest_sha256"] == file_sha(baseline / "manifest.json")
    assert sorted(path.name for path in output.iterdir()) == ["model", "reviewed-switch.json"]
    with pytest.raises(InputError, match="already exists"):
        package_reviewed_switch.package_candidate(lock, output)


def test_package_leaves_no_candidate_when_the_locked_gate_fails(tmp_path, locked_comparison):
    lock, _, _, metrics = locked_comparison
    metrics["candidate_passed"] = False
    output = tmp_path / "candidate"
    with pytest.raises(InputError, match="did not pass"):
        package_reviewed_switch.package_candidate(lock, output)
    assert not output.exists()


def test_submission_verifies_the_bundled_policy_and_evidence():
    verified = verify_submission()
    assert verified["mixed_alert_cutoff"] == 0.35
    assert verified["word_threshold"] == 0.10


def test_submission_rejects_changed_aggregate_counts(tmp_path):
    submission = tmp_path / "submission"
    copytree(Path("release/submission"), submission)
    path = submission / "reviewed-switch.json"
    evidence = read_json(path)
    evidence["results"]["policies"]["candidate"]["switch"]["false_positive"] = 0
    write_json(path, evidence)
    with pytest.raises(InputError, match="aggregate results differ"):
        verify_submission(submission)
