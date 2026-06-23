#!/usr/bin/env python3
"""Generate a concept-practice PPTX and run the standard validation chain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from generate_concept_practice_deck import generate_deck
from validate_editable_deck import inspect_deck as inspect_editable_deck
from validate_generation_report import validate_report
from validate_ooxml_style_parts import inspect_deck as inspect_ooxml_style_deck
from validate_reference_pattern import inspect_deck as inspect_reference_pattern
from validate_reference_pattern import validate as validate_reference_pattern


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def decide_require_blank_shapes(generation_report: dict, explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    quality = generation_report.get("quality_summary", {})
    return int(quality.get("source_square_blank_count", 0) or 0) > 0


def run_build(
    pdf_path: Path,
    page_range: str,
    output_path: Path,
    report_dir: Path,
    *,
    require_blank_shapes: bool | None = None,
    allow_report_warnings: bool = False,
) -> dict:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

    generation_report = generate_deck(pdf_path, page_range, output_path)
    write_json(report_dir / "generation-report.json", generation_report)

    generation_validation = validate_report(generation_report, allow_warnings=allow_report_warnings)
    write_json(report_dir / "generation-report-validation.json", generation_validation)

    editable_report = inspect_editable_deck(output_path)
    write_json(report_dir / "editable-report.json", editable_report)

    ooxml_style_report = inspect_ooxml_style_deck(output_path, SKILL_DIR)
    write_json(report_dir / "ooxml-style-report.json", ooxml_style_report)

    require_blanks = decide_require_blank_shapes(generation_report, require_blank_shapes)
    reference_args = SimpleNamespace(
        require_animations=True,
        require_group_animation=True,
        require_blank_shapes=require_blanks,
        forbid_visible_page_labels=True,
        forbid_off_slide_objects=True,
    )
    pattern_report = validate_reference_pattern(inspect_reference_pattern(output_path), reference_args)
    write_json(report_dir / "pattern-report.json", pattern_report)

    validations = {
        "generation_report": generation_validation.get("passes") is True,
        "editable_deck": editable_report.get("passes") is True,
        "ooxml_style": ooxml_style_report.get("passes") is True,
        "reference_pattern": pattern_report.get("passes") is True,
    }
    build_report = {
        "passes": all(validations.values()),
        "output_pptx": str(output_path),
        "report_dir": str(report_dir),
        "require_blank_shapes": require_blanks,
        "validations": validations,
        "generation_summary": generation_validation.get("summary", {}),
        "editable_failures": editable_report.get("failures", []),
        "ooxml_style_failures": ooxml_style_report.get("failures", []),
        "pattern_failures": pattern_report.get("failures", []),
        "generation_failures": generation_validation.get("failures", []),
    }
    write_json(report_dir / "build-summary.json", build_report)
    return build_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a concept-practice PPTX and run report/editable/reference-pattern validation."
    )
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--pages", required=True, help="Page range, e.g. 28-59 or 28~59")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--report-dir",
        type=Path,
        help="Directory for generation, validation, and build-summary JSON reports.",
    )
    parser.add_argument(
        "--require-blank-shapes",
        dest="require_blank_shapes",
        action="store_true",
        default=None,
        help="Force reference-pattern validation to require blank shapes.",
    )
    parser.add_argument(
        "--no-require-blank-shapes",
        dest="require_blank_shapes",
        action="store_false",
        help="Force reference-pattern validation not to require blank shapes.",
    )
    parser.add_argument(
        "--allow-report-warnings",
        action="store_true",
        help="Do not fail the generation report validation when quality_summary warnings are present.",
    )
    args = parser.parse_args(argv)

    report_dir = args.report_dir or args.output.parent / f"{args.output.stem}_reports"
    build_report = run_build(
        args.pdf,
        args.pages,
        args.output,
        report_dir,
        require_blank_shapes=args.require_blank_shapes,
        allow_report_warnings=args.allow_report_warnings,
    )
    print(json.dumps(build_report, ensure_ascii=False, indent=2))
    return 0 if build_report["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
