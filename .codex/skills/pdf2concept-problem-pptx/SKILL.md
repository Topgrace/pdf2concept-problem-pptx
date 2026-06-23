---
name: pdf2concept-problem-pptx
description: Convert math concept-book PDFs into 16:9 lecture PPTX decks by extracting only "개념익히기" practice problems from specified PDF pages and reconstructing them as editable text, math text, shapes, and animations that follow the skill's built-in reference-derived design pattern. Use when the user asks to turn middle-school or high-school math PDF problem sections into teaching slides, especially requests like "PDF 10~50쪽에서 개념익히기 문제만 뽑아서 같은 패턴의 강의용 PPTX로 만들어줘." Do not use full-problem screenshots or cropped problem-block images as the main slide content unless the user explicitly requests image-only slides.
---

# PDF Concept Problems to PPTX

## Workflow

1. Identify the source PDF, target page range, and output PPTX path.
   - For ordinary page-range requests, use `scripts/build_concept_practice_deck.py` first. This is the standard build runner: it calls the generic generator, writes the generation report, runs report/editable/OOXML-style/reference-pattern validators, and fails the build if the output does not satisfy the skill contract.
2. Use the internal design contract in `assets/design/style-map.json` as the default runtime style source. Inspect an external reference PPTX only when the user explicitly provides one for calibration; do not require, copy, or read a reference PPTX at runtime for normal skill use.
3. Extract only blocks labeled "개념익히기" or equivalent concept-practice headings from the requested PDF pages. Ignore examples, explanations, unit summaries, unrelated exercises, answer keys, workbook sections, `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` unless the user explicitly asks for them.
4. Build a problem inventory with source page number, section title, problem prompt, subproblem numbers, subproblem text, math notation, source layout type, row/column positions, diagrams/images, actual square blanks found in the PDF, and any visible answer/solution. Separate the prompt from subproblems before slide layout. Mark source answers, worked examples, and red-filled guide answers separately from problem text.
5. Create the PPTX through the skill renderer and built-in assets/style maps. After the editable slide objects are written, inject the built-in style-only OOXML parts from `assets/concept-practice-style/ooxml-style-parts` so generated decks carry the measured theme, master, layout, presentation properties, view properties, and table style parts without reading a raw reference deck. Use the injected master/layout background and problem panel as the only background/panel source; do not draw duplicate full-slide backgrounds or large white panels as slide-local objects.
6. Generate slides using editable text boxes, math-formatted text runs, lines, arrows, blank boxes, circles, and grouped reveal objects that match the skill's common reference pattern.
7. Use images only for atomic diagrams, graphs, icons, or source illustrations that are not practical to redraw. Do not paste a full problem area, full page, or complete exercise block as one image.
8. Verify every included problem came from the requested page range and every excluded item is outside the "개념익히기" scope.
9. Inspect the generator report's `slide_trace` and `quality_summary` when adding or validating a page family. `slide_trace` must identify actual slide numbers, source page/practice, chunk index, item numbers, default-visible item, and click-reveal order. `quality_summary.warning_count` should be treated as a review queue; resolve extraction/layout warnings when they point to real slide defects. `quality_summary.normalizations` records intentional renderer corrections such as row-major ordering for two-column PDF text extraction.
10. Let `scripts/build_concept_practice_deck.py` run the standard validators before delivery. If running validators manually, run `scripts/validate_generation_report.py <report.json>`, `scripts/validate_editable_deck.py <output.pptx>`, `scripts/validate_ooxml_style_parts.py <output.pptx>`, and `scripts/validate_reference_pattern.py <output.pptx> --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects`. Add `--require-blank-shapes` only when the source problems contain actual square blanks. If any validator fails, rebuild the deck rather than explaining the failure away.
11. Render or visually inspect the produced PPTX enough to confirm slide count, 16:9 dimensions, Korean text rendering, media links, no text overlap/clipping, no visible page numbers, no unnecessary square blanks, and reference-style layout/animation reuse on the actual slide canvas. Fix issues before providing only the final PPTX.

## Generic Page-Range Generation

Use `scripts/build_concept_practice_deck.py` for normal requests such as pages 28-59, 62-79, or any range that is not a hard-coded deterministic reproduction case.

Run:

```bash
python scripts/build_concept_practice_deck.py --pdf <input.pdf> --pages <start-end> --output <output.pptx> --report-dir <report-dir>
```

This build runner is the broad default entrypoint. Its runtime pipeline is:

`PDF page range -> concept-practice extraction -> PracticeBlock IR -> design-contract renderer -> OOXML style injection -> group-animation XML -> generation report -> report/editable/OOXML-style/reference-pattern validation -> build summary`.

It:

- reads the requested PDF pages with PyMuPDF,
- includes only pages where `개념 익히기` is detected,
- excludes `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` pages,
- creates 16:9 editable PPTX slides with title slides, prompt text, grouped item rows, and no problem-block screenshots,
- adds `p:set` reveal animations whose targets are `p:grpSp` groups,
- records included and excluded source pages in the report.
- records actual problem slide numbers, chunk indexes, default-visible and click-reveal item order, and extraction quality warnings in the report.
- automatically requires blank-shape validation when the source inventory contains square blanks.
- writes `generation-report.json`, `generation-report-validation.json`, `editable-report.json`, `ooxml-style-report.json`, `pattern-report.json`, and `build-summary.json` under the report directory.

Use `scripts/generate_concept_practice_deck.py` directly only when debugging extraction/rendering before the validation chain.

For the verified `중등수학 2-1본문학생용(001-188)_SPOT.pdf` pages 10-19 case, still use this same generic generator:

```bash
python scripts/build_concept_practice_deck.py --pdf <input.pdf> --pages 10-19 --output <output.pptx> --report-dir <report-dir>
```

The generic generator contains an embedded unit 1 pages 10-19 style/content plan and records `generation_mode: unit1_10_19_embedded_style_plan` in the report. Do not call a separate legacy unit-specific generator; that standalone script is not part of the skill runtime.

The generic generator uses heuristic PDF text extraction, but it must still apply the same built-in slide design pattern. If a page family needs tighter visual reproduction, add measured layout rules to `assets/design/style-map.json` and renderer support for that layout family instead of making the skill depend on a runtime reference PPTX.

## PPTX Construction Rules

- Match the built-in design contract first, then make problem content readable.
- Use the built-in master/layout background exactly as supplied by the OOXML style parts. Title slides must be linked to the title layout, problem slides must be linked to the problem layout, and generated slides must not add slide-local full-canvas background rectangles or large white content panels over those layouts.
- For subunit cover slides, reproduce the measured reference cover structure rather than centering title text manually. The large concept number must be made from two overlaid `나눔스퀘어 ExtraBold` text boxes at the same coordinates: the back number uses blue fill plus a thick blue text outline, and the front number uses `bg1` fill with no outline. Do not render the concept number as one plain blue text box.
- The cover `개념핵심` label must be a small yellow rounded rectangle above the concept number, with a separate no-wrap blue label text box. Use the measured label size and placement from `assets/design/style-map.json`; do not replace it with a wide pill, plain text, or centered fallback button.
- Preserve the source PDF's problem-body layout whenever it affects readability. The built-in reference-derived design contract supplies theme, header style, fonts, and animation behavior, but it must not force a different item arrangement when the PDF clearly uses a different structure.
- Keep Korean lecture slides legible from a classroom screen: large problem numbers, clear line spacing, and uncluttered formulas.
- Preserve original mathematical meaning exactly. Do not simplify, rewrite, or solve problems unless the user asks for 풀이 or 정답 slides.
- Do not show source answers or worked example answers in a problem-only PPTX unless the user explicitly asks for answers. Red text in the PDF, such as filled-in example numbers, decimal answers, `유한소수`, `무한소수`, `순`, `유`, or completed solution text, is answer content by default.
- If red answer text fills a source blank, preserve the blank shape and hide the red answer text. For example, a PDF row showing `5/9 = [5] ÷ [9] = 0.555... (무한소수)` should become `5/9 = [ ] ÷ [ ] = (        )` in the problem slide.
- If the built-in style map for a page family uses one problem per slide, follow that. If it defines problem plus staged explanation slides, reproduce that sequence.
- Keep the prompt and subproblems separate. Put enough vertical space below the prompt so the first subproblem never overlaps with prompt text; split to the next slide when subproblems are too many or too tall.
- Position the first subproblem from the prompt textbox bottom using the measured `problem_slide.item.prompt_gap` value in `assets/design/style-map.json`; do not use a fixed first-row y-value that can collide with long prompts.
- If the PDF problem block is a vertical one-column list, keep it as a vertical one-column list on the slide, with source-like row spacing and a separate right-side answer column. Do not convert it into a two-column grid only because a reference slide has two columns.
- If the PDF problem block is a two-column grid, table, worked-solution stack, or number-line layout, preserve that source arrangement as closely as the slide canvas allows. Split across slides instead of shrinking text or rearranging rows in a way that changes the reading flow.
- For `two_column_grid` IR without source boxes or explicit right-column items, treat the item order as the layout source: place items by `column = index % 2` and `row = index // 2`. Do not treat the default `column_index=0` on every item as an explicit instruction to stack all items in the left column.
- Preserve the PDF line structure in the item inventory. When a subproblem is extracted from multiple source lines, keep those source lines in `PracticeItem.source_lines`, derive separate `PracticeItem.display_lines`, and split each display line into typed `PracticeItem.display_segments` such as `math` and `korean_label`. Korean label segments such as `순환마디:`, `간단히 표현:`, and `분모의 소인수:` use the same Korean font as prompt text, not the math font. Do not split a one-line embedded/reference-planned expression into multiple rows only because it contains several equals signs.
- For two-column worked-solution blocks, order rendered items and click reveals by visual row first, then column, so the reading order follows the slide layout rather than raw PDF text extraction order.
- If a two-column worked-solution block contains multiline items, split each visual row into its own slide chunk, usually `(1)(2)` then `(3)(4)`, instead of forcing all rows onto one slide. Reset row positioning inside each continuation slide so the first displayed row starts at the normal first-row position.
- When a source item is drawn as a vertical worked stack, use coordinates to recover the semantic expression before rendering. Do not expose PDF extraction artifacts such as `+>²`, `->²`, or `1 5×5×5×5`; convert these into readable editable math such as `+(a+4b-2)`, `-(3a+10b+2)`, or `1/(5×5×5×5)`.
- Use `나눔스퀘어라운드 ExtraBold` first for Korean prompt text and match the built-in measured prompt textbox style: `24pt` font, `150%` paragraph line spacing, and the prompt box coordinates/heights in `assets/design/style-map.json`. When a prompt wraps to multiple lines, wrap only at spaces/word boundaries; do not split Korean words into syllables or split Latin/math tokens in the middle. Use bold `BT수식M` first for formulas and math expressions.
- Reconstruct fractions with horizontal fraction bars when the PDF shows fractions; do not flatten them into slash notation when a stacked fraction is needed for readability or reference fidelity.
- For recurring-decimal shorthand, match the reference deck's ellipsis character. In the unit 1 reference deck, decimal continuations use the single horizontal ellipsis `…` (`U+2026`), not three baseline periods `...`; using three periods makes the marks sit too low.
- Keep stacked-fraction font size consistent within the same problem section and slide family. Do not make one-digit fractions such as `1/7` or `1/5` smaller than two-digit fractions such as `19/10`; use the same math font size, fraction bar thickness, numerator/denominator textbox height, and vertical offsets unless the reference deck explicitly uses a different size for a different semantic role.
- Align each stacked fraction to the subproblem number baseline for the relevant reference pattern. In page 10-style conversion rows, the numerator is only slightly above the problem-number textbox, the fraction bar is near the lower part of the number row, and the denominator sits just below the bar. Do not use page 15 factorization-fraction offsets for page 10 conversion rows.
- In chained equality formulas, align stacked fraction bars to the visual centerline of the adjacent equals signs. In the unit 1 page 14 `개념 익히기 1` pattern, do not reuse page 15 factorization offsets; the fraction bar must sit near the equals baseline while numerator text stays above and denominator text or denominator blanks sit below.
- Give every stacked fraction enough width for the longest numerator or denominator. Multi-digit numerator/denominator text such as `19` and `10` must stay on one line above/below the fraction bar and must never wrap into vertical digits.
- When generating stacked fractions with editable text boxes, set the numerator and denominator boxes to no-wrap behavior, size them from the measured text length, and center-align the numerator/denominator text inside the shared fraction-width box before drawing the fraction bar. Do not use a fixed narrow fraction template for two-digit or longer values.
- Keep stacked fractions vertically balanced: unless a measured layout override explicitly says otherwise, make the vertical whitespace between the numerator textbox bottom and fraction bar equal to the whitespace between the fraction bar bottom and denominator textbox top.
- Split inline math operators and parenthesis answer blanks into separate editable text objects, then center-align each object inside its textbox. Preserve the source/IR whitespace inside parenthesis answer blanks exactly: for example, render `= (        )` as one `=` text object followed by one `(        )` text object, not as a combined `= (        )` textbox and not normalized to `( )`; apply the same split rule to `=`, `÷`, and `×`. Size parenthesis answer-blank text boxes by character slot width: `width = k * len(token)`, where `k = font_size / 72 * math.answer_parenthesis_char_em`; this keeps `(`, every preserved space, and `)` inside the textbox bounds.
- Render exponents as superscript text runs. Do not leave source expressions as caret notation such as `2^2`, `5^3`, or `2^5` in the visible slide text.
- Match the reference deck's exponent run style, not just the character content. In the unit 1 reference deck, denominator expressions such as `2^2×3×5` use a single denominator textbox with base runs at `BT수식M` 24pt, exponent runs at 20pt, and `baseline=60000`. Avoid separate low-positioned exponent textboxes for normal factorization denominators.
- Place the fraction bar and denominator using the reference vertical relationship: for page 15-style factorization fractions, the fraction bar sits almost level with the problem-number baseline, the numerator is clearly above it, and the denominator textbox begins just below it. Do not push the whole fraction down so the exponent appears beside the base instead of above it.
- For page 15-style two-column factorization grids, use the measured reference row and answer-column coordinates. Do not shift the first row upward or push the right answer parentheses into the blue side background; keep the top row around the reference problem-number baseline and reveal/space rows as full item groups.
- Reconstruct each subproblem formula as one readable inline math row. Keep equals signs, division symbols, decimal parts, and answer parentheses on the same baseline unless the source PDF intentionally stacks them.
- Size editable inline numeric math tokens from the built-in width contract, not the raw character-count estimate alone. Decimal tokens such as `0.15` and recurring-decimal tokens such as `3.232323…` must receive the `math.inline_numeric_width_scale` and `math.inline_numeric_width_padding` allowance from `assets/design/style-map.json` so bold `BT수식M` text is not clipped by a too-narrow text box.
- Keep animations consistent with the reference. If direct animation authoring is unreliable, duplicate animated reference slides and replace their text/image content.
- Keep the first example or first subproblem visible by default. Group later subproblems so they appear one by one on click in reading order.
- "Visible by default" means the first problem row or example structure is visible, not that source answer text is visible. Hide example answers unless producing an answer/solution deck.
- Reference reveals target grouped objects (`p:grpSp`), not loose individual text boxes. When duplicating an animated slide, keep each reveal step as a group and update the group's child text/shapes. Do not leave `p:set` timing attached to an unrelated title, problem number, or single text box.
- Every `p:set` timing target must resolve to an existing slide object id. For the measured reference style, each `style.visibility` reveal target should be a group that contains the item/answer/step to appear.
- Do not set `hidden="1"` on `p:set` reveal target groups. The PowerPoint slideshow engine uses the timing tree to hide entrance targets before their click step; marking the group itself hidden can make clicks skip the target and advance to the next slide.
- Each animated subproblem group must include its problem number, formula/text, answer blank or answer text, and helper text/shapes for that item.
- The animated group bounds must cover the full source-like row for that item. For vertical-list problems, reveal one full row at a time: problem number, formula, inline blanks, and right answer column together.
- During reference analysis, ignore fully off-slide objects when matching the reference pattern. Do not copy or create those objects in the generated deck.
- Generated decks must not contain unrelated objects whose bounding boxes are fully or partially outside the 16:9 slide canvas. When duplicating a template slide, delete off-canvas helper objects, copied page labels, spare title chips, and unrelated timing targets before writing the final PPTX.
- For scanned PDFs, use OCR/manual reconstruction for text and math. Use rendered crops only as a temporary extraction aid or for isolated diagrams.
- For diagrams, graphs, tables, and geometric figures, preserve the original visual as a small atomic image only when a clean editable reconstruction would be less accurate.
- Do not create slide bodies where the problem content is a single large screenshot/crop. That output does not match this skill's reference pattern.
- Do not represent answer blanks with literal square characters such as `□`. Recreate blanks as editable rounded-rectangle/rectangle shapes matching the source position and reference style only when the source PDF contains actual square blanks. If the PDF has no square blank, do not invent one. Parenthesis blanks such as `(    )` may remain text only when the source/reference uses that form for the same problem type.
- Match reference square-blank shape styling, including border weight. For the unit 1 page 10 reference, inline blank boxes are about `0.551in x 0.551in` with line width `31750` EMU and a visibly dark gray outline; thin pale borders are not acceptable.
- Parenthesis answer blanks must remain on one line. Use a wide no-wrap text box matching the reference answer column; do not let the closing parenthesis wrap to the next line.
- Place square blank shapes at the same semantic location as the PDF. For example, if the source row is `1/7 = □ ÷ □ =`, the two blank boxes must sit immediately after `=` and after `÷` inside the formula row, not in the answer column or at the end of the expression.
- Preserve square blanks inside stacked-fraction denominators. For denominator factorization rows such as `3/(□^2×□)` or `11/(□^2×□^2)`, draw the blank boxes inside the denominator under the fraction bar and place the exponent as a small raised text object immediately to the upper-right of the corresponding blank. Do not replace the blanks with the hidden answer factors.
- Treat outer parentheses around multiplicative denominator groups as structural grouping, not visible text. For example, `3/([ ]²×[ ])` should render as one stacked fraction whose denominator is `[ ]²×[ ]`, without showing `(` or `)` under the fraction bar.
- When a PDF shows square blanks with red numbers inside them, remove the red numbers and keep empty square blank shapes at those exact positions.
- Do not display source page numbers on the slide canvas. Keep source page trace data in the build report or non-visible metadata only.
- Name outputs clearly, usually with source PDF stem and page range.

## Validation

Run this once before sharing or after changing the skill package:

```bash
python scripts/self_check_skill.py --report <self-check-report.json>
```

Run this after generating any non-exact-reference deck:

```bash
python scripts/build_concept_practice_deck.py --pdf <input.pdf> --pages <start-end> --output <output.pptx> --report-dir <report-dir>
```

If validating a deck manually instead of using the build runner:

```bash
python scripts/validate_generation_report.py <report.json> --report <generation-report-validation.json>
python scripts/validate_editable_deck.py <output.pptx> --report <editable-report.json>
python scripts/validate_ooxml_style_parts.py <output.pptx> --report <ooxml-style-report.json>
python scripts/validate_reference_pattern.py <output.pptx> --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects --report <pattern-report.json>
```

For the unit 1 pages 10-19 embedded style plan, also open the output in Microsoft PowerPoint when PowerPoint is available and export at least slides 7 and 8 to PNG. The generated deck must open without repair, corruption, or missing-relationship errors before it is considered valid.

The deck is not acceptable if problem slides have no editable text and rely on one large inserted image.
The deck is also not acceptable if on-slide reference-style animations target loose text boxes instead of groups, if timing targets are missing, if visible page labels remain, if unrelated objects sit outside the slide canvas, if generated slides contain slide-local duplicate background/panel overlays, if source one-column problem rows were rearranged into an unreadable grid, if source inline square blanks moved away from their formula position, if red source answer/example text is visible in a problem-only deck, if stacked fraction digits wrap vertically because the text box is too narrow, or if on-slide square blanks are typed as `□` characters. When the source problems contain actual square blanks, add `--require-blank-shapes` and require at least one non-title problem slide to contain reference-style blank shapes. Do not add `--require-blank-shapes` when the source PDF has no square blanks. Fully off-slide helper/template objects may be ignored while analyzing a reference PPTX, but generated PPTX files must pass `--forbid-off-slide-objects`.

## Reference

Read `references/design-contract.md` before changing the generator architecture or adding a new layout family.

Read `references/conversion-checklist.md` when performing an actual conversion or when deciding how to extract problems and preserve PPTX animations.

Read `references/reference-style-analysis.md` only as a measured style note from prior analysis. Do not require or look for raw reference input files at runtime.

Read `references/unit1-10-19-style-map.md` when maintaining or validating the embedded unit 1 pages 10-19 style plan inside `scripts/generate_concept_practice_deck.py`.
