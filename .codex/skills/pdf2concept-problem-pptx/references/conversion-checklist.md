# Conversion Checklist

## Inputs

- Source PDF path
- Requested page range, using the PDF viewer's page numbering unless the user specifies printed page numbers
- Reference PPTX path, only when the user explicitly provides one or the requested workflow requires matching an external deck
- Output PPTX path
- Whether to include problem-only slides, solution slides, answer summary slides, or all of them
- For independent deterministic generation, use bundled measured assets/style data under `assets/unit1-10-19/` and the matching generator script; do not require raw reference input PDFs/PPTX files at runtime.
- For all other generated decks, run `../scripts/validate_editable_deck.py <output.pptx>` and `../scripts/validate_reference_pattern.py <output.pptx> --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects`; require `"passes": true` from both reports. Add `--require-blank-shapes` only when the source problems contain actual square blanks.

## PDF Extraction

1. Inspect the page range visually or with text extraction before bulk processing.
2. Search for headings such as `개념익히기`, `개념 익히기`, `개념 확인`, or a known book-specific variant.
3. For text PDFs, use structured extraction where possible and preserve math symbols, superscripts, fractions, and Korean spacing.
4. For scanned PDFs, render target pages to images for reading/OCR, then reconstruct the slide as editable text, math text, and shapes.
5. Use image crops only for atomic diagrams, graphs, QR-like icons, or illustrations; never use a full problem block crop as the slide body unless the user explicitly asks for image-only slides.
6. Split each `개념 익히기` block into prompt and subproblems before layout.
7. Record the source layout for each problem block: one-column vertical list, two-column grid, table, worked stack, number line, diagram layout, or mixed layout. Keep row baselines, left formula column, and right answer column relationships when reconstructing.
8. Mark whether each source problem contains actual square blanks and record each blank's semantic anchor, such as "after equals sign" or "after division symbol." If a blank contains red guide-answer text, keep the blank shape but remove the red text. Do not create square blank shapes for problems that do not have them in the PDF.
9. Exclude `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` unless explicitly requested.
10. Keep a trace table in the report: problem id, source page, extraction source, source layout type, editable slide objects created, and slide number. Do not show source page numbers on slide canvas.

## Reference PPTX Analysis

1. Check slide dimensions and confirm 16:9.
2. Identify repeated slide patterns: title, problem, explanation, answer, section divider.
3. Record fonts, font sizes, text colors, accent colors, margins, and alignment.
4. Inspect slide masters/layouts and reuse them when possible.
5. Preserve animations by copying the reference PPTX and duplicating existing slides or XML parts when the deck relies on motion effects.
6. Confirm reveal targets are grouped slide objects (`p:grpSp`) and not loose text boxes.
7. Record whether square blanks are represented as rounded-rectangle shapes in the reference or as parenthesis text.
8. Ignore reference objects whose bounding boxes are fully outside the slide canvas; do not copy them into the generated deck.
9. Record prompt font, prompt line spacing, formula font, and item spacing.

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
- Render or visually inspect the final deck before delivery; fix issues and provide only the final corrected PPTX.
- Confirm fully off-slide helper/template objects from the reference were ignored during analysis and removed from generated slides.
- Save the final deck as `.pptx`.
