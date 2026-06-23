# Conversion Checklist

## Inputs

- Source PDF path
- Requested page range, using the PDF viewer's page numbering unless the user specifies printed page numbers
- Reference PPTX path, only when the user explicitly provides one for calibration. Normal runtime generation must use the skill's internal design contract, not a copied reference deck.
- Output PPTX path
- Whether to include problem-only slides, solution slides, answer summary slides, or all of them
- Before sharing or after changing the skill package, run `../scripts/self_check_skill.py --report <self-check-report.json>` and require `"passes": true`.
- For ordinary page-range conversion, run `../scripts/build_concept_practice_deck.py --pdf <input.pdf> --pages <start-end> --output <output.pptx> --report-dir <report-dir>` first. This is the default build runner; it extracts detected `개념 익히기` blocks, normalizes them to `PracticeBlock` IR, applies `../assets/design/style-map.json`, injects built-in OOXML style parts, writes editable grouped slides with reveal animations, and runs the standard validation chain.
- For the verified unit 1 pages 10-19 case, still run `../scripts/build_concept_practice_deck.py --pdf <input.pdf> --pages 10-19 --output <output.pptx> --report-dir <report-dir>`. The generic generator behind this runner contains an embedded unit 1 style/content plan and must not call a separate legacy unit-specific script.
- The build runner writes `generation-report.json`, `generation-report-validation.json`, `editable-report.json`, `ooxml-style-report.json`, `pattern-report.json`, and `build-summary.json`; require `"passes": true` from `build-summary.json`.
- Use `../scripts/generate_concept_practice_deck.py` directly only when debugging extraction/rendering before running the full build.
- After generation, inspect the generator report's `quality_summary` and `slide_trace`. `quality_summary.warning_count` is not an automatic failure, but each warning must be checked against the produced deck before delivery. `quality_summary.normalizations` should explain intentional corrections, such as row-major ordering for two-column source extraction.

## PDF Extraction

1. Inspect the page range visually or with text extraction before bulk processing.
2. Search for headings such as `개념익히기`, `개념 익히기`, `개념 확인`, or a known book-specific variant.
3. For text PDFs, use structured extraction where possible and preserve math symbols, superscripts, fractions, and Korean spacing.
4. For scanned PDFs, render target pages to images for reading/OCR, then reconstruct the slide as editable text, math text, and shapes.
5. Use image crops only for atomic diagrams, graphs, QR-like icons, or illustrations; never use a full problem block crop as the slide body unless the user explicitly asks for image-only slides.
6. Split each `개념 익히기` block into prompt and subproblems before layout.
7. Record the source layout for each problem block: one-column vertical list, two-column grid, table, worked stack, number line, diagram layout, or mixed layout. Keep row baselines, left formula column, and right answer column relationships when reconstructing.
8. Preserve per-item source line structure in the inventory. If a subproblem spans several source lines, keep those lines with the item and render them as multiple editable math rows inside one reveal group. Do not split one-line reference-planned expressions merely because they contain several equals signs.
9. Mark whether each source problem contains actual square blanks and record each blank's semantic anchor, such as "after equals sign" or "after division symbol." If a blank contains red guide-answer text, keep the blank shape but remove the red text. Do not create square blank shapes for problems that do not have them in the PDF.
10. Exclude `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` unless explicitly requested.
11. Keep a trace table in the report: problem id, source page, extraction source, source layout type, source lines, editable slide objects created, and slide number. Do not show source page numbers on slide canvas.
12. Confirm report slide traces include actual slide numbers, chunk indexes, item numbers, default-visible item numbers, and click-reveal item numbers.

## Design Contract And Optional Reference Analysis

1. Read `design-contract.md` before changing the generator architecture.
2. Treat `../assets/design/style-map.json` as the runtime source of common slide coordinates, fonts, colors, and animation intent.
3. Do not reference local expected-output files or raw reference PPTX files from runtime scripts or skill instructions.
4. Add measured values to the design map when repeated source-layout families need tighter fidelity.

## Optional Reference PPTX Analysis

1. Check slide dimensions and confirm 16:9.
2. Identify repeated slide patterns: title, problem, explanation, answer, section divider.
3. Record fonts, font sizes, text colors, accent colors, margins, and alignment.
4. Inspect slide masters/layouts only to extract reusable style data. Do not make the generated deck depend on the raw reference file.
5. Confirm reveal targets are grouped slide objects (`p:grpSp`) and not loose text boxes.
6. Record whether square blanks are represented as rounded-rectangle shapes in the reference or as parenthesis text.
7. Ignore reference objects whose bounding boxes are fully outside the slide canvas; do not copy them into the generated deck.
8. Record prompt font, prompt line spacing, formula font, and item spacing.

## Output Quality

- Do not mix unrelated design styles.
- Match the PDF source problem-body layout before applying reference slide item grids. If a source problem is a vertical one-column list, keep one item per row with source-like row spacing and the answer parentheses aligned in a right-side answer column.
- Hide source answer/example text in problem-only decks. Treat red filled-in values, red decimals, and red answer words such as `무한소수` as answers, not as problem text.
- Do not use full-page screenshots or large problem-block crops when the reference style expects editable text and grouped reveal objects.
- Do not include non-`개념익히기` exercises unless explicitly requested.
- Exclude `개념 다지기` and `개념 마무리` pages unless the user explicitly asks for them.
- Check that every slide has enough contrast and no overlapping text.
- Confirm that media files are embedded and not linked to missing local paths.
- Confirm problem slides contain editable text/shape content, not only a generated PNG/JPEG.
- Confirm on-slide reference-style reveal animations target groups and have no missing `p:spTgt` ids.
- Confirm on-slide square blanks are shape objects, not typed `□` characters.
- Confirm square blank shapes appear only where the source PDF had actual square blanks.
- Confirm square blank shapes sit at the same formula position as the PDF, especially blanks between `=`, `÷`, and the final `=` in conversion exercises.
- Confirm square blank shapes that contained red guide answers in the PDF are empty in the generated problem slide.
- Confirm red source answers or example answers are not visible unless the requested output includes answers or solution slides.
- Confirm source page numbers are not visible on slide canvas.
- Confirm no generated slide object sits fully or partially outside the slide canvas unless the user explicitly requested an intentional bleed object.
- Confirm prompt text uses `나눔스퀘어라운드 ExtraBold` when available, formulas use `BT수식M` when available, and fractions use horizontal fraction bars when the PDF shows stacked fractions.
- Confirm every stacked fraction has enough width for the longest numerator/denominator and uses no-wrap text boxes; `19/10` must render as `19` over `10`, not as `1` over `9` over `0`.
- Confirm prompt/subproblem spacing, line spacing, and item spacing follow the source PDF layout where it affects readability, while retaining the reference deck's visual style and animation pattern.
- Confirm two-column worked-solution blocks render and reveal in visual row-major order, not raw PDF text extraction order.
- Confirm dense two-column worked-solution blocks with multiline items are split by visual row when needed, and continuation slides reset the row y-position instead of starting halfway down the slide.
- Confirm multiline worked-solution items are grouped as one reveal step containing all rows for that subproblem.
- Confirm the generator report has no unexplained quality warnings for missing item numbers, duplicate item numbers, unknown layout, empty prompts, missing source lines, or slide trace count mismatches.
- Confirm `validate_generation_report.py` passes, proving that requested pages are fully accounted for, included/excluded page sets do not overlap, slide traces cover every inventory item, chunk indexes are contiguous, and default/reveal item order is internally consistent.
- Render or visually inspect the final deck before delivery; fix issues and provide only the final corrected PPTX.
- Confirm fully off-slide helper/template objects from the reference were ignored during analysis and removed from generated slides.
- Confirm `self_check_skill.py` passes before committing or sharing the skill folder; it verifies required files, JSON validity, Python compile status, asset/style-part manifest hashes, and absence of removed runtime dependencies.
- Save the final deck as `.pptx`.
