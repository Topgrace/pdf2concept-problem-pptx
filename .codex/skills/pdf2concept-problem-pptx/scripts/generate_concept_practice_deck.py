#!/usr/bin/env python3
"""Generate an editable concept-practice PPTX from a math PDF page range."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from src.design import load_design
from src.extract import (
    EXPECTED_UNIT1_PDF_SHA256,
    UNIT1_10_19_BLOCKS,
    UNIT1_10_19_EXCLUDED,
    extract_practice_blocks,
    parse_page_range,
    sha256_file,
)
from src.render import build_presentation
from src.report import build_report


def generate_deck(pdf_path: Path, page_range: str, output_path: Path) -> dict:
    start_page, end_page = parse_page_range(page_range)
    source_sha256 = sha256_file(pdf_path)
    design = load_design(SKILL_DIR)

    if start_page == 10 and end_page == 19 and source_sha256 == EXPECTED_UNIT1_PDF_SHA256:
        blocks = UNIT1_10_19_BLOCKS
        excluded = UNIT1_10_19_EXCLUDED
        generation_mode = "unit1_10_19_embedded_style_plan"
    else:
        blocks, excluded = extract_practice_blocks(pdf_path, start_page, end_page)
        generation_mode = "generic_pdf_text_extraction"

    if not blocks:
        raise SystemExit("No concept-practice blocks were found in the requested range.")

    deck_info = build_presentation(blocks, output_path, design)
    deck_info["generation_mode"] = generation_mode
    return build_report(pdf_path, page_range, source_sha256, blocks, excluded, deck_info)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an editable concept-practice PPTX from a PDF page range.")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--pages", required=True, help="Page range, e.g. 28-59 or 28~59")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    if not args.pdf.exists():
        raise SystemExit(f"Input PDF not found: {args.pdf}")

    report = generate_deck(args.pdf, args.pages, args.output)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
