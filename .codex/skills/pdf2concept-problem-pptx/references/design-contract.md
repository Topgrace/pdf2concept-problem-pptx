# Design Contract

This skill should generate concept-practice PPTX decks from PDF source pages using a stable internal design contract rather than a runtime reference PPTX.

## Pipeline

1. Source PDF and requested pages are parsed.
2. Pages outside `개념 익히기` scope are excluded.
3. Each detected block is normalized to `PracticeBlock` IR:
   - source page
   - concept number and title
   - practice number
   - prompt
   - ordered subproblem items
   - source extraction lines for reporting/debugging
   - layout type, currently `vertical_list`, `two_column_grid`, `worked_stack`, or `unknown`
   - item inventory with problem number, expression text, square blank count, parenthesis blank flag, fraction/exponent flags, source PDF bounding box, row index, and column index
   - per-item `source_lines` preserving the PDF line structure for multiline rows
   - per-item `display_lines` derived from those source lines so separate PDF lines become separate editable PPTX text/math rows
   - per-item `display_segments` typed as `math` or `korean_label` so mixed rows can use the correct font per segment
4. The renderer applies `assets/design/style-map.json` to create 16:9 editable PPTX slides.
5. The math renderer converts common slash fractions and superscript text into editable text boxes, fraction bars, and blank shapes.
6. Style-only OOXML assets are injected after PPTX creation: theme, slide masters, slide layouts, presentation properties, view properties, and table styles. Generated title slides are redirected to the built-in title layout, and generated problem slides are redirected to the built-in problem layout while preserving actual slide content and slide order. Backgrounds and content panels come from those master/layout parts, not from duplicate slide-local overlay shapes.
7. Reveal animations are injected as group-targeted `p:set` timing nodes.
8. Validation checks editable text, embedded OOXML style parts, group animation, no visible page labels, no off-slide objects, and blank-shape requirements.
9. Report validation checks that requested pages are accounted for, included/excluded page sets are consistent, slide traces cover the normalized item inventory, pagination chunks are contiguous, and quality warnings are resolved or explicitly allowed.
10. The standard build runner writes all validation reports and fails unless generation-report, editable-deck, OOXML-style, and reference-pattern validation all pass.
11. Skill package self-check validates required files, JSON files, Python source compilation, bundled asset hashes, and absence of removed runtime dependencies before sharing.

## Runtime Design Source

- `assets/design/style-map.json` is the common runtime style source.
- `assets/concept-practice-style/` contains extracted reusable title/header images and style-only OOXML from prior reference analysis. These assets are general concept-practice style assets, not a page-range-specific runtime dependency.
- `assets/concept-practice-style/ooxml-style-parts/` is applied at runtime to generated PPTX packages. It must be validated against `style-parts-manifest.json` before sharing the skill.
- Generated slides must rely on the injected master/layout backgrounds and panels. Do not add full-canvas background rectangles or large problem-panel shapes directly to slide XML when the style parts already provide them.
- Raw reference PPTX files must not be required at runtime.
- Local expected-output folders are evaluation aids only and must not be referenced by skill instructions or runtime scripts.

## Extension Rules

- Add measured values to `assets/design/style-map.json` when a recurring layout family is found.
- Add extractor fields to the IR before adding renderer-specific hacks.
- Preserve source PDF layout type first: one-column list, two-column grid, chained equality, table, diagram, or mixed layout.
- Preserve item-level source line structure before rendering. Multiline rows should keep `source_lines`, derive `display_lines`, and split those lines into typed `display_segments` before rendering. Math segments should stay editable math, and Korean label segments should use the same Korean font as prompt text. One-line embedded/reference-planned rows should remain inline even when they contain several equals signs.
- For two-column blocks, render and animate items in visual row-major order after extraction normalizes row and column indexes.
- For two-column blocks that have no source boxes and no explicit right-column items, derive grid positions from display order (`column = index % 2`, `row = index // 2`) instead of treating the default `column_index=0` as authoritative.
- For two-column worked blocks with multiline items, paginate by visual row to avoid overcrowding. Each continuation slide should normalize its local row index so the first row starts at the standard first-row y position.
- Reports must include the normalized block/item inventory so layout and math-extraction failures can be audited without opening the PPTX.
- Reports must include actual problem slide numbers, block chunk indexes, item numbers, default-visible item numbers, and click-reveal item numbers so animation order and pagination can be audited without opening the PPTX.
- Reports must include a `quality_summary` with source block/item counts, title/problem slide counts, source blank/fraction/exponent/multiline counts, intentional normalizations, and non-fatal warnings for suspicious extraction conditions.
- Math rendering should stay editable: use text boxes, rectangle bars, superscript runs, and blank shapes instead of equation screenshots.
- Inline numeric math tokens should use the style-map numeric width allowance (`math.inline_numeric_width_scale`, `math.inline_numeric_width_padding`, and `math.inline_numeric_min_w`) after the base character-width estimate. This keeps bold `BT수식M` decimal text such as `0.15` from exceeding its editable text box.
- Keep formulas editable. Use atomic images only for diagrams or figures that are not practical to redraw.
- If a generated deck differs from the expected visual pattern, update the design map and renderer rather than making the skill depend on a reference deck copy.
