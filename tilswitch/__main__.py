from __future__ import annotations

import argparse
import sys
from pathlib import Path
from time import perf_counter

from .types import InputError, RunConfig, json_dump

CONFIG = Path("conf/experiment.json")


def _configuration(parser):
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--source-set", choices=("tatoeba", "flores"))


def _commands() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tilswitch", description="Train, evaluate or run TilSwitch AI.")
    commands = parser.add_subparsers(dest="command", required=True)
    fetch = commands.add_parser("fetch", help="Fetch public data and record source hashes")
    _configuration(fetch)
    group = fetch.add_mutually_exclusive_group()
    group.add_argument("--review-only", action="store_true")
    group.add_argument("--mono-only", action="store_true")
    prepare = commands.add_parser("prepare", help="Prepare grouped train/dev/test splits")
    _configuration(prepare)

    review = commands.add_parser("review", help="Export or validate blind review TSVs")
    actions = review.add_subparsers(dest="review_action", required=True)
    for action in ("export", "validate"):
        review_command = actions.add_parser(action)
        _configuration(review_command)
        review_command.add_argument("--dataset", choices=("krcs", "authored"), default="krcs")
        review_command.add_argument("--split", choices=("dev", "test"), required=True)

    train = commands.add_parser("train", help="Fit and save a CPU model")
    _configuration(train)
    train.add_argument("--model", choices=("word", "context"), required=True)

    lock = commands.add_parser("lock", help="Lock model choices and held-out digests")
    _configuration(lock)
    lock.add_argument("--out", type=Path, required=True)
    lock.add_argument("--datasets", nargs="+", choices=("mono", "krcs", "authored"), default=["mono"])

    evaluate = commands.add_parser("evaluate", help="Evaluate development data or a locked holdout")
    _configuration(evaluate)
    evaluate.add_argument("--phase", choices=("dev", "test"), required=True)
    evaluate.add_argument("--lock", type=Path)
    evaluate.add_argument("--out", type=Path)

    release = commands.add_parser("release", help="Package the chosen model and locked inference policy")
    _configuration(release)
    release.add_argument("--lock", type=Path, required=True)
    release.add_argument("--out", type=Path, required=True)

    analyze = commands.add_parser("analyze", help="Analyze one message and emit JSON")
    analyze.add_argument("--bundle", type=Path, default=Path("release/model"))
    analyze.add_argument("--heuristic", action="store_true", help="Use the script and letter baseline")
    message = analyze.add_mutually_exclusive_group(required=True)
    message.add_argument("--text")
    message.add_argument("--file", type=Path, help="Read the original message from a UTF-8 file")

    demo = commands.add_parser("demo", help="Launch the local browser interface")
    demo.add_argument("--bundle", type=Path, default=Path("release/model"))
    demo.add_argument("--port", type=int, default=7860)
    bench = commands.add_parser("benchmark", help="Measure local cold load and warm inference")
    bench.add_argument("--bundle", type=Path, default=Path("release/model"))
    return parser


def _run(args):
    command = args.command
    if hasattr(args, "config"):
        cfg = RunConfig.load(args.config, args.source_set)
    if command == "fetch":
        from .sources import fetch_sources
        return fetch_sources(cfg, review_only=args.review_only, mono_only=args.mono_only)
    if command == "prepare":
        from .prepare import prepare
        return prepare(cfg)
    if command == "review":
        from .prepare import export_review, validate_review
        if args.review_action == "export":
            path, messages = export_review(cfg, args.dataset, args.split)
            return {"path": str(path), "messages": messages}
        path, receipt = validate_review(cfg, args.dataset, args.split)
        return {"path": str(path), **receipt}
    if command == "train":
        from .train import train
        path, receipt = train(cfg, args.model)
        return {"path": str(path), **receipt}
    if command == "lock":
        from .evaluate import create_lock
        lock = create_lock(cfg, args.out, tuple(dict.fromkeys(args.datasets)))
        return {"path": str(args.out), "release_model": lock["release_model"], "informal_dev": lock["informal_dev"],
                "test": lock["test"]}
    if command == "evaluate":
        from .evaluate import evaluate_dev, evaluate_test
        if args.phase == "dev":
            out = args.out or cfg.runs / "dev.json"
            result = evaluate_dev(cfg, out)
        else:
            if args.lock is None or args.out is None:
                raise InputError("Test evaluation requires --lock and a new --out directory.")
            out = args.out / "summary.json"
            result = evaluate_test(cfg, args.lock, args.out)
        return {"report": str(out), "release_model": result["release_model"], "informal_dev": result["informal_dev"]}
    if command == "release":
        from .evaluate import make_release
        return make_release(cfg, args.lock, args.out)
    if command == "analyze":
        from .infer import analyze
        from .model import load_bundle
        raw = args.text if args.text is not None else args.file.read_bytes().decode("utf-8-sig")
        return analyze(raw, None if args.heuristic else load_bundle(args.bundle))
    if command == "demo":
        from .demo import launch
        launch(args.bundle, args.port)
        return None
    if command == "benchmark":
        from .evaluate import benchmark
        from .model import load_bundle
        from .samples import EXAMPLES
        started = perf_counter()
        model = load_bundle(args.bundle)
        cold_ms = 1000 * (perf_counter() - started)
        short = [text for _, text in EXAMPLES]
        near_limit = [((text + " ") * (1000 // (len(text) + 1))).strip() for text in short]
        return {"model_id": model.model_id, "bundle_load_ms": cold_ms,
                "short": benchmark(model, short * 10), "near_limit": benchmark(model, near_limit * 10)}
    raise AssertionError(f"Unexpected command: {command}")


def main(argv=None) -> int:
    args = _commands().parse_args(argv)
    try:
        result = _run(args)
        if result is not None:
            print(json_dump(result))
    except (ValueError, TypeError, KeyError) as error:
        print(f"TilSwitch: {error}", file=sys.stderr)
        return 2
    except (OSError, ImportError) as error:
        print(f"TilSwitch: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
