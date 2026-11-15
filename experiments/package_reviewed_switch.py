"""Package the candidate from the frozen comparison of Mixed alert cutoffs."""

import argparse
from dataclasses import replace
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from .reviewed_switch import score
from tilswitch.model import Policy, load_bundle, save_bundle
from tilswitch.types import InputError, file_sha, json_dump, new_artifact_dir, read_json, write_json


def package_candidate(lock_path: Path, output: Path) -> dict:
    with new_artifact_dir(output) as folder:
        with TemporaryDirectory(dir=folder) as directory:
            replay = Path(directory)
            copyfile(lock_path, replay / "lock.json")
            score(replay)
            inputs = read_json(replay / "lock.json")["inputs"]
            metrics_path = replay / "score" / "metrics.json"
            metrics = read_json(metrics_path)
            provenance = {
                "lock_sha256": metrics["lock_sha256"],
                "metrics_sha256": file_sha(metrics_path),
                "baseline_manifest_sha256": inputs["bundle_manifest_sha256"],
                "annotations_sha256": inputs["annotations_sha256"],
            }
        if metrics["candidate_passed"] is not True:
            raise InputError("The candidate did not pass the locked switch comparison.")

        baseline_path = Path(inputs["bundle"])
        baseline = load_bundle(baseline_path, provenance["baseline_manifest_sha256"])
        candidate = replace(
            baseline,
            model_id=f"{baseline.model_id}-switch-{provenance['lock_sha256'][:10]}",
            policy=Policy(**inputs["policies"]["candidate"]),
        )
        bundle = folder / "model"
        metadata = read_json(baseline_path / "metadata.json")
        save_bundle(bundle, candidate, {**metadata, "switch_comparison": provenance})
        manifest = read_json(bundle / "manifest.json")
        if any(manifest.get(name) != digest for name, digest in read_json(baseline_path / "manifest.json").items()
               if name not in {"metadata.json", "policy.json"}):
            raise InputError("The candidate changed an asset used to label words.")
        manifest_sha = file_sha(bundle / "manifest.json")
        measured = load_bundle(bundle, manifest_sha)
        if measured.policy != candidate.policy or measured.model_id != candidate.model_id:
            raise InputError("The packaged model differs from the candidate in the lock.")

        write_json(folder / "reviewed-switch.json", {
            "candidate_model_id": candidate.model_id,
            "candidate_manifest_sha256": manifest_sha,
            "policies": inputs["policies"],
            "provenance": provenance,
            "results": metrics,
        })
    return {"model": str(output / "model"), "model_id": candidate.model_id,
            "manifest_sha256": manifest_sha, "evidence": str(output / "reviewed-switch.json")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json_dump(package_candidate(args.lock, args.out)))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"TilSwitch: {error}\n")
