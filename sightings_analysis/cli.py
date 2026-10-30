from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .analysis import analyze_rows, load_rows
from .context import AnalysisContext
from .integrity import verify_manifest, write_manifest
from .privacy import scan
from .reporting import write_outputs
from .synthetic_data import DEFAULT_ROWS, DEFAULT_SEED, write_csv
from .template_data import write_template
from .validation import validate_reports

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepare_output(path: Path, *, force: bool) -> bool:
    if path.exists() and any(path.iterdir()):
        if not force:
            print("Output directory already contains files.", file=sys.stderr)
            print(f"  {path}", file=sys.stderr)
            print("Use --force to replace the existing output.", file=sys.stderr)
            return False
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return True


def _print_validation_failure(result: dict[str, Any]) -> None:
    print("Validation failed.", file=sys.stderr)
    print(file=sys.stderr)
    for item in result["blocking_errors"][:8]:
        location = f" (row {item['row']})" if "row" in item else ""
        print(f"- {item['message']}{location}", file=sys.stderr)
    remaining = len(result["blocking_errors"]) - 8
    if remaining > 0:
        print(f"- ...and {remaining} additional blocking findings", file=sys.stderr)
    print(file=sys.stderr)
    print("Your source file was not modified.", file=sys.stderr)
    print("See: docs/data-schema.md", file=sys.stderr)


def _print_warning_summary(result: dict[str, Any], *, limit: int = 10) -> None:
    if not result["warnings"]:
        return
    print("Warning categories:")
    for code, count in result["warning_summary"].items():
        print(f"  {code}: {count}")
    examples = result["warnings"][:limit]
    print()
    print(f"Showing the first {len(examples)} example(s):")
    for item in examples:
        location = f"row {item['row']}: " if "row" in item else ""
        print(f"  - {location}{item['message']}")
    remaining = len(result["warnings"]) - len(examples)
    if remaining > 0:
        print(f"  ...and {remaining} additional warning(s)")


def _print_validation_summary(result: dict[str, Any], reports: Path) -> None:
    if result["blocking_errors"]:
        _print_validation_failure(result)
        return
    print("Validation passed.")
    print()
    print("Records:")
    print(f"  {result['row_count']:,}")
    if result.get("date_coverage"):
        print()
        print("Date coverage:")
        print(
            f"  {result['date_coverage']['start']} to {result['date_coverage']['end']}"
        )
    print()
    print("Warnings:")
    print(f"  {result['warning_count']}")
    print("Material warnings:")
    print(f"  {result['material_warning_count']}")
    if result["warnings"]:
        print()
        _print_warning_summary(result)
    print()
    print("Your source file was not modified.")
    print()
    print("Next:")
    command = (
        "python -m sightings_analysis analyze "
        f"--reports \"{reports}\" --output reports/my-analysis"
    )
    if result["material_warning_count"]:
        command += " --allow-warnings"
    print(f"  {command}")


def _execute_analysis(
    source: Path,
    output: Path,
    *,
    validation: dict[str, Any],
    context: AnalysisContext,
    seed: int | None,
) -> int:
    rows = load_rows(source)
    analysis = analyze_rows(rows)
    outputs = write_outputs(
        output,
        source_path=source,
        validation=validation,
        analysis=analysis,
        context=context,
        seed=seed,
    )

    print("UFO/UAP Sightings Analysis complete.")
    print()
    if context.dataset_type == "synthetic":
        print("Records generated:")
        print(f"  {analysis['input_rows']:,} synthetic reports")
        print()
    print("Records analyzed:")
    print(f"  {analysis['input_rows']:,}")
    print()
    print("Quality findings:")
    print(f"  {validation['warning_count']} warnings")
    print(f"  {validation['blocking_error_count']} blocking errors")
    print()
    print("Open first:")
    print(f"  {outputs['summary']}")
    print()
    print("Figures:")
    print(f"  {output / 'figures'}/")
    print()
    print("Reproducibility evidence:")
    print(f"  {outputs['manifest']}")
    print()
    if context.dataset_type == "synthetic":
        print("No external, scraped, or personal data was used.")
    else:
        print("The source dataset was read without modification.")
    return 0


def run_demo(output: Path, *, force: bool) -> int:
    if not _prepare_output(output, force=force):
        return 4
    source = output / "input" / "synthetic-reports.csv"
    write_csv(source, rows=DEFAULT_ROWS, seed=DEFAULT_SEED)
    validation = validate_reports(source)
    if validation["blocking_errors"]:
        _print_validation_failure(validation)
        return 2
    return _execute_analysis(
        source,
        output,
        validation=validation,
        context=AnalysisContext.synthetic_demo(),
        seed=DEFAULT_SEED,
    )


def run_analysis(
    source: Path,
    output: Path,
    *,
    allow_warnings: bool,
    force: bool,
) -> int:
    result = validate_reports(source)
    if result["blocking_errors"]:
        _print_validation_failure(result)
        return 2
    if result["material_warning_count"] and not allow_warnings:
        print("Validation completed with material warnings.", file=sys.stderr)
        print(file=sys.stderr)
        print(f"Material warnings: {result['material_warning_count']}", file=sys.stderr)
        print(
            "Review the warnings with the validate command, then rerun with "
            "--allow-warnings if appropriate.",
            file=sys.stderr,
        )
        print("Your source file was not modified.", file=sys.stderr)
        return 3
    if not _prepare_output(output, force=force):
        return 4
    return _execute_analysis(
        source,
        output,
        validation=result,
        context=AnalysisContext.user_supplied(),
        seed=None,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sightings-analysis",
        description="Validate and analyze reported UFO/UAP sighting datasets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser(
        "demo",
        help="Run the deterministic synthetic demonstration.",
    )
    demo.add_argument(
        "--output",
        type=Path,
        default=Path.cwd() / "reports" / "demo",
    )
    demo.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output directory.",
    )

    template = subparsers.add_parser(
        "template",
        help="Create a ready-to-edit CSV template and field guide.",
    )
    template.add_argument("--output", type=Path, required=True)
    template.add_argument("--force", action="store_true")

    validate = subparsers.add_parser(
        "validate",
        help="Validate an authorized report CSV without modifying it.",
    )
    validate.add_argument("--reports", type=Path, required=True)
    validate.add_argument("--output", type=Path, help="Optional JSON report path.")
    validate.add_argument(
        "--json",
        action="store_true",
        help="Print complete machine-readable JSON instead of the human summary.",
    )

    analyze = subparsers.add_parser(
        "analyze",
        help="Analyze a validated report CSV.",
    )
    analyze.add_argument("--reports", type=Path, required=True)
    analyze.add_argument("--output", type=Path, required=True)
    analyze.add_argument("--allow-warnings", action="store_true")
    analyze.add_argument("--force", action="store_true")

    scan_parser = subparsers.add_parser(
        "privacy-scan",
        help="Scan a release tree for common public-boundary risks.",
    )
    scan_parser.add_argument("path", type=Path, nargs="?", default=PROJECT_ROOT)

    subparsers.add_parser(
        "verify-release",
        help="Verify repository files against RELEASE_MANIFEST.json.",
    )
    build_manifest = subparsers.add_parser(
        "build-release-manifest",
        help="Regenerate RELEASE_MANIFEST.json for a maintainer release.",
    )
    build_manifest.add_argument("--force", action="store_true")
    return parser


def _run_command(args: argparse.Namespace) -> int:
    if args.command == "demo":
        return run_demo(args.output.resolve(), force=args.force)

    if args.command == "template":
        output = args.output.resolve()
        guide = output.with_name(f"{output.stem}-README.md")
        existing = [path for path in (output, guide) if path.exists()]
        if existing and not args.force:
            print("Template output already exists.", file=sys.stderr)
            for path in existing:
                print(f"  {path}", file=sys.stderr)
            print("Use --force to replace it.", file=sys.stderr)
            return 4
        paths = write_template(output)
        print("Template created.")
        print()
        print(f"CSV:   {paths[0]}")
        print(f"Guide: {paths[1]}")
        return 0

    if args.command == "validate":
        reports = args.reports.resolve()
        result = validate_reports(reports)
        rendered = json.dumps(result, indent=2, sort_keys=True)
        if args.json:
            print(rendered)
        else:
            _print_validation_summary(result, reports)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            if not args.json:
                print()
                print(f"Complete JSON report: {args.output}")
        return 0 if not result["blocking_errors"] else 2

    if args.command == "analyze":
        return run_analysis(
            args.reports.resolve(),
            args.output.resolve(),
            allow_warnings=args.allow_warnings,
            force=args.force,
        )

    if args.command == "privacy-scan":
        findings = scan(args.path.resolve())
        print(
            json.dumps(
                {"status": "passed" if not findings else "failed", "findings": findings},
                indent=2,
            )
        )
        return 0 if not findings else 1

    if args.command == "verify-release":
        findings = verify_manifest(PROJECT_ROOT)
        print(
            json.dumps(
                {"status": "passed" if not findings else "failed", "findings": findings},
                indent=2,
            )
        )
        return 0 if not findings else 1

    if args.command == "build-release-manifest":
        path = PROJECT_ROOT / "RELEASE_MANIFEST.json"
        if path.exists() and not args.force:
            print("RELEASE_MANIFEST.json already exists.", file=sys.stderr)
            print("Use --force to regenerate it after reviewing release changes.", file=sys.stderr)
            return 4
        written = write_manifest(PROJECT_ROOT)
        print(f"Release manifest written: {written}")
        return 0

    return 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run_command(args)
    except KeyboardInterrupt:
        print("Operation cancelled. No source file was modified.", file=sys.stderr)
        return 130
    except (OSError, ValueError, csv.Error) as exc:
        print("The command could not be completed.", file=sys.stderr)
        print(file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        print(file=sys.stderr)
        print("No source file was modified.", file=sys.stderr)
        return 5
