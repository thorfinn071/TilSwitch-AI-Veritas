"""Verify the submission bundle and its aggregate evidence from a clean checkout."""

import json
from dataclasses import asdict, replace
from pathlib import Path

from tilswitch.model import load_bundle
from tilswitch.types import InputError, file_sha, json_dump, read_json, text_sha

DIAGNOSTIC_EVIDENCE = Path("release/evidence/holdout-56.json")
DIAGNOSTIC_SHA256 = "4dddaeee555e644f3873820677605060cd03dc1b62ac1a396f7718dcd178e83c"


def verify_submission(submission: Path = Path("release/submission"), reference: Path = Path("release/model")) -> dict:
    evidence = read_json(submission / "reviewed-switch.json")
    provenance = evidence["provenance"]
    results = evidence["results"]
    bundle = submission / "model"
    candidate = load_bundle(bundle, evidence["candidate_manifest_sha256"])
    baseline = load_bundle(reference, provenance["baseline_manifest_sha256"])

    if (candidate.model_id != evidence["candidate_model_id"]
            or read_json(bundle / "metadata.json")["switch_comparison"] != provenance):
        raise InputError("The submission model does not match the evidence provenance.")
    policies = {"baseline": asdict(baseline.policy), "candidate": asdict(candidate.policy)}
    if (policies != evidence["policies"] or baseline.policy.threshold != 0.10
            or baseline.policy.singleton_switch_margin != 0.20
            or candidate.policy != replace(baseline.policy, singleton_switch_margin=0.35)):
        raise InputError("The submission policy does not match the evaluated 0.35 candidate.")

    candidate_files = read_json(bundle / "manifest.json")
    baseline_files = read_json(reference / "manifest.json")
    for name in ("weights.npz", "vocabulary.json", "word-evidence.json"):
        if candidate_files[name] != baseline_files[name]:
            raise InputError(f"The submission changed a word-labeling asset: {name}.")

    serialized_results = json.dumps(results, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if (results["candidate_passed"] is not True or results["lock_sha256"] != provenance["lock_sha256"]
            or text_sha(serialized_results) != provenance["metrics_sha256"]):
        raise InputError("The aggregate results differ from the locked comparison.")
    return {"model_id": candidate.model_id, "manifest_sha256": evidence["candidate_manifest_sha256"],
            "word_threshold": candidate.policy.threshold, "mixed_alert_cutoff": candidate.policy.singleton_switch_margin}


if __name__ == "__main__":
    try:
        result = verify_submission()
        if file_sha(DIAGNOSTIC_EVIDENCE) != DIAGNOSTIC_SHA256:
            raise InputError("The 56-message diagnostic evidence differs from the contest version.")
        diagnostic = read_json(DIAGNOSTIC_EVIDENCE)
        if diagnostic["model_manifest_sha256"] != result["manifest_sha256"]:
            raise InputError("The diagnostic evidence refers to a different model bundle.")
        print(json_dump({**result, "diagnostic_reference": diagnostic["reference_provenance"]["kind"]}))
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"TilSwitch: {error}") from None
