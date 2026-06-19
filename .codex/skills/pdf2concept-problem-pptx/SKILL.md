---
name: pdf2concept-problem-pptx
description: Convert math concept-book PDFs into 16:9 lecture PPTX decks by extracting only "개념익히기" practice problems from specified PDF pages and reconstructing them as editable text, math text, shapes, and animations that match a provided reference PPTX. Use when the user asks to turn middle-school or high-school math PDF problem sections into teaching slides, especially requests like "PDF 10~50쪽에서 개념익히기 문제만 뽑아서 참고 PPTX와 같은 패턴으로 만들어줘." Do not use full-problem screenshots or cropped problem-block images as the main slide content unless the user explicitly requests image-only slides.
---

# PDF Concept Problems to PPTX

## Workflow

1. Identify the source PDF, target page range, output PPTX path, and reference PPTX. If the user asks to match a reference deck but no reference PPTX is available, ask for it before creating the final deck.
   - If the request is the verified unit 1 PDF pages 10-19 case, use `scripts/generate_unit1_10_19.py` first. This deterministic path does not need or read the human-made reference PPTX at runtime.
2. Inspect the reference PPTX before extracting problems. Record slide size, fonts, colors, reusable layouts, title/body positions, problem/solution slide sequence, transitions, and animation behavior.
3. Extract only blocks labeled "개념익히기" or equivalent concept-practice headings from the requested PDF pages. Ignore examples, explanations, unit summaries, unrelated exercises, answer keys, workbook sections, `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` unless the user explicitly asks for them.
4. Build a problem inventory with source page number, section title, problem prompt, subproblem numbers, subproblem text, math notation, source layout type, row/column positions, diagrams/images, actual square blanks found in the PDF, and any visible answer/solution. Separate the prompt from subproblems before slide layout. Mark source answers, worked examples, and red-filled guide answers separately from problem text.
5. Create the PPTX from a copy of the reference PPTX when animation or layout fidelity matters. Preserve the reference deck's masters, theme, fonts, transitions, and animation XML wherever possible instead of starting from a blank presentation.
6. Generate slides using editable text boxes, math-formatted text runs, lines, arrows, blank boxes, circles, and grouped reveal objects that match the reference pattern.
7. Use images only for atomic diagrams, graphs, icons, or source illustrations that are not practical to redraw. Do not paste a full problem area, full page, or complete exercise block as one image.
8. Verify every included problem came from the requested page range and every excluded item is outside the "개념익히기" scope.
9. Run `scripts/validate_editable_deck.py <output.pptx>` and `scripts/validate_reference_pattern.py <output.pptx> --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects` before delivery. Add `--require-blank-shapes` only when the source problems contain actual square blanks. If either validator fails, rebuild the deck rather than explaining the failure away.
10. Render or visually inspect the produced PPTX enough to confirm slide count, 16:9 dimensions, Korean text rendering, media links, no text overlap/clipping, no visible page numbers, no unnecessary square blanks, and reference-style layout/animation reuse on the actual slide canvas. Fix issues before providing only the final PPTX.

## Unit 1 Pages 10-19 Independent Generation

Use `scripts/generate_unit1_10_19.py` when the input PDF is the verified `중등수학 2-1본문학생용(001-188)_SPOT.pdf` and the requested range is pages 10-19.

Run:

```bash
python scripts/generate_unit1_10_19.py --pdf <input.pdf> --output <output.pptx> --report <report.json>
```

This generator is independent of `중2-1-1단원 개념익히기_참고용.pptx`. The human-made PPTX was used only to measure the style, coordinates, image assets, theme/master/layout parts, and animation pattern. Runtime generation writes a new PPTX package directly from encoded OOXML, embeds only assets from `assets/unit1-10-19/`, and records `runtime_reference_pptx_used: false` in the report.

Keep `assets/unit1-10-19/presentation-metadata.xml` in the deterministic package. It is stripped presentation metadata from the analyzed deck with embedded-font references removed; it supplies PowerPoint-compatible presentation defaults, slide IDs, and master IDs. Do not replace it with a minimal generated `ppt/presentation.xml`, because PowerPoint can treat that output as corrupted even when simpler parsers accept it.

The generator has strict font preflight by default. It expects `나눔스퀘어라운드 ExtraBold` and `BT수식M` to be installed for stable rendering on another computer. Use `--allow-missing-fonts` only for validation-only runs where visual parity is not being judged.

Read `references/unit1-10-19-style-map.md` before changing this deterministic generator.

## PPTX Construction Rules

- Match the reference deck first, then make problem content readable.
- For subunit cover slides, reproduce the measured reference cover structure rather than centering title text manually. In the unit 1 reference deck, slide 1 uses a large `01` made from two overlaid number text boxes: a blue `나눔스퀘어 ExtraBold` number with a thick blue text outline, then a `bg1` fill number above it. The `개념핵심` label is a small yellow rounded rectangle above the number/title group.
- Preserve the source PDF's problem-body layout whenever it affects readability. The reference PPTX supplies theme, header style, fonts, and animation behavior, but it must not force a different item arrangement when the PDF clearly uses a different structure.
- Keep Korean lecture slides legible from a classroom screen: large problem numbers, clear line spacing, and uncluttered formulas.
- Preserve original mathematical meaning exactly. Do not simplify, rewrite, or solve problems unless the user asks for 풀이 or 정답 slides.
- Do not show source answers or worked example answers in a problem-only PPTX unless the user explicitly asks for answers. Red text in the PDF, such as filled-in example numbers, decimal answers, `유한소수`, `무한소수`, `순`, `유`, or completed solution text, is answer content by default.
- If red answer text fills a source blank, preserve the blank shape and hide the red answer text. For example, a PDF row showing `5/9 = [5] ÷ [9] = 0.555... (무한소수)` should become `5/9 = [ ] ÷ [ ] = (        )` in the problem slide.
- If the reference deck uses one problem per slide, follow that. If it uses problem plus staged explanation slides, reproduce that sequence.
- Keep the prompt and subproblems separate. Put enough vertical space below the prompt so the first subproblem never overlaps with prompt text; split to the next slide when subproblems are too many or too tall.
- If the PDF problem block is a vertical one-column list, keep it as a vertical one-column list on the slide, with source-like row spacing and a separate right-side answer column. Do not convert it into a two-column grid only because a reference slide has two columns.
- If the PDF problem block is a two-column grid, table, worked-solution stack, or number-line layout, preserve that source arrangement as closely as the slide canvas allows. Split across slides instead of shrinking text or rearranging rows in a way that changes the reading flow.
- Use `나눔스퀘어라운드 ExtraBold` first for Korean prompt text and match the reference prompt textbox line spacing. Use `BT수식M` first for formulas and math expressions.
- Reconstruct fractions with horizontal fraction bars when the PDF shows fractions; do not flatten them into slash notation when a stacked fraction is needed for readability or reference fidelity.
- For recurring-decimal shorthand, match the reference deck's ellipsis character. In the unit 1 reference deck, decimal continuations use the single horizontal ellipsis `…` (`U+2026`), not three baseline periods `...`; using three periods makes the marks sit too low.
- Keep stacked-fraction font size consistent within the same problem section and slide family. Do not make one-digit fractions such as `1/7` or `1/5` smaller than two-digit fractions such as `19/10`; use the same math font size, fraction bar thickness, numerator/denominator textbox height, and vertical offsets unless the reference deck explicitly uses a different size for a different semantic role.
- Align each stacked fraction to the subproblem number baseline for the relevant reference pattern. In page 10-style conversion rows, the numerator is only slightly above the problem-number textbox, the fraction bar is near the lower part of the number row, and the denominator sits just below the bar. Do not use page 15 factorization-fraction offsets for page 10 conversion rows.
- In chained equality formulas, align stacked fraction bars to the visual centerline of the adjacent equals signs. In the unit 1 page 14 `개념 익히기 1` pattern, do not reuse page 15 factorization offsets; the fraction bar must sit near the equals baseline while numerator text stays above and denominator text or denominator blanks sit below.
- Give every stacked fraction enough width for the longest numerator or denominator. Multi-digit numerator/denominator text such as `19` and `10` must stay on one line above/below the fraction bar and must never wrap into vertical digits.
- When generating stacked fractions with editable text boxes, set the numerator and denominator boxes to no-wrap behavior and size them from the measured text length before drawing the fraction bar. Do not use a fixed narrow fraction template for two-digit or longer values.
- Render exponents as superscript text runs. Do not leave source expressions as caret notation such as `2^2`, `5^3`, or `2^5` in the visible slide text.
- Match the reference deck's exponent run style, not just the character content. In the unit 1 reference deck, denominator expressions such as `2^2×3×5` use a single denominator textbox with base runs at `BT수식M` 24pt, exponent runs at 20pt, and `baseline=60000`. Avoid separate low-positioned exponent textboxes for normal factorization denominators.
- Place the fraction bar and denominator using the reference vertical relationship: for page 15-style factorization fractions, the fraction bar sits almost level with the problem-number baseline, the numerator is clearly above it, and the denominator textbox begins just below it. Do not push the whole fraction down so the exponent appears beside the base instead of above it.
- For page 15-style two-column factorization grids, use the measured reference row and answer-column coordinates. Do not shift the first row upward or push the right answer parentheses into the blue side background; keep the top row around the reference problem-number baseline and reveal/space rows as full item groups.
- Reconstruct each subproblem formula as one readable inline math row. Keep equals signs, division symbols, decimal parts, and answer parentheses on the same baseline unless the source PDF intentionally stacks them.
- Keep animations consistent with the reference. If direct animation authoring is unreliable, duplicate animated reference slides and replace their text/image content.
- Keep the first example or first subproblem visible by default. Group later subproblems so they appear one by one on click in reading order.
- "Visible by default" means the first problem row or example structure is visible, not that source answer text is visible. Hide example answers unless producing an answer/solution deck.
- Reference reveals target grouped objects (`p:grpSp`), not loose individual text boxes. When duplicating an animated slide, keep each reveal step as a group and update the group's child text/shapes. Do not leave `p:set` timing attached to an unrelated title, problem number, or single text box.
- Every `p:set` timing target must resolve to an existing slide object id. For the measured reference style, each `style.visibility` reveal target should be a group that contains the item/answer/step to appear.
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
- When a PDF shows square blanks with red numbers inside them, remove the red numbers and keep empty square blank shapes at those exact positions.
- Do not display source page numbers on the slide canvas. Keep source page trace data in the build report or non-visible metadata only.
- Name outputs clearly, usually with source PDF stem and page range.

## Validation

Run this after generating any non-exact-reference deck:

```bash
python scripts/validate_editable_deck.py <output.pptx> --report <editable-report.json>
python scripts/validate_reference_pattern.py <output.pptx> --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects --report <pattern-report.json>
```

For the unit 1 pages 10-19 deterministic generator, also open the output in Microsoft PowerPoint when PowerPoint is available and export at least slides 7 and 8 to PNG. The generated deck must open without repair, corruption, or missing-relationship errors before it is considered valid.

The deck is not acceptable if problem slides have no editable text and rely on one large inserted image.
The deck is also not acceptable if on-slide reference-style animations target loose text boxes instead of groups, if timing targets are missing, if visible page labels remain, if unrelated objects sit outside the slide canvas, if source one-column problem rows were rearranged into an unreadable grid, if source inline square blanks moved away from their formula position, if red source answer/example text is visible in a problem-only deck, if stacked fraction digits wrap vertically because the text box is too narrow, or if on-slide square blanks are typed as `□` characters. When the source problems contain actual square blanks, add `--require-blank-shapes` and require at least one non-title problem slide to contain reference-style blank shapes. Do not add `--require-blank-shapes` when the source PDF has no square blanks. Fully off-slide helper/template objects may be ignored while analyzing a reference PPTX, but generated PPTX files must pass `--forbid-off-slide-objects`.

## Reference

Read `references/conversion-checklist.md` when performing an actual conversion or when deciding how to extract problems and preserve PPTX animations.

Read `references/reference-style-analysis.md` only as a measured style note from prior analysis. Do not require or look for raw reference input files at runtime.

Read `references/unit1-10-19-style-map.md` when maintaining or validating the independent unit 1 pages 10-19 generator.
