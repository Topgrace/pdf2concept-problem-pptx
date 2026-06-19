# Reference Style Analysis

## Measured Reference Style Notes

These notes record style and extraction behavior measured from earlier human-made/reference decks. They are retained as documentation only. The independent skill must not require raw reference input PDFs or PPTX files at runtime.

The original sample conversion scope was PDF pages 62-79, which became a 22-slide PPTX.

## Extraction Pattern From PDF Pages 62-79

- Include only `개념 익히기` blocks from `개념핵심` sections.
- Exclude `개념 다지기`, `개념 마무리`, and `학교 시험 준비하기` pages even when they are inside the requested page range, unless the user explicitly asks for them.
- Do not show source page numbers on the slide canvas. Preserve source page numbers only in the build report or non-visible metadata. Older reference slides may contain off-canvas page labels; do not copy them into generated slides.
- Treat fully off-slide objects as helper/template artifacts, not required visible slide content. The reference deck contains off-canvas objects such as page labels and extra header-like objects; ignore them during analysis and remove them from generated slides.
- In the sample:
  - Slide 1 introduces `12. 부등식`; slides 2-5 cover `개념 익히기` from pages 62-63.
  - Slide 6 introduces `13. 부등식의 성질`; slide 7 covers page 67.
  - Slide 8 introduces `14. 일차부등식의 풀이`; slides 9-11 cover pages 70-71.
  - Slide 12 introduces `15. 여러 가지 일차부등식의 풀이`; slides 13-14 cover page 74.
  - Slide 15 introduces `16. 일차부등식의 활용`; slides 16-22 cover pages 77-79.

## Slide Size And Theme

- Use 16:9 widescreen: `12192000 x 6858000 EMU`, equal to `13.333in x 7.5in`.
- Reuse the reference PPTX theme and masters instead of creating a blank deck.
- Main Korean font: `나눔스퀘어라운드 ExtraBold`.
- Main math font: `BT수식M`.
- Theme fallback includes `맑은 고딕`.
- Title slides use large `40pt` text; normal problem text is usually `24pt`.
- Page labels use `28pt`; title-chip text uses `10.5pt`; some number-line labels use `20pt`.
- Primary blue: `#275184`; highlight yellow: `#F9EA5B`; red emphasis for `○`, `×`, and similar marks: `#FF0000`.

## Layout Pattern

- Use a title slide at the start of each concept section: `개념핵심` label plus concept number/title.
- Title slide reference positions:
  - `개념핵심` label near `x=2.449in, y=2.341in`.
  - Main concept title near `x=2.477in, y=2.788in`.
  - Character/image decoration around `x=9.143in, y=2.360in` or `x=11.592in, y=2.360in` depending on the title slide.
- Problem slides use a top-left header image around `x=0.283in, y=0.528in, w=1.937in, h=0.463in`. Preserve this image from the template.
- Standard prompt text starts around `x=0.224in, y=0.993in, w=9.56in, h=0.65in`.
- Prompt text uses `나눔스퀘어라운드 ExtraBold`; match the reference prompt textbox line spacing and keep the prompt/subproblem gap large enough to prevent overlap.
- Long word-problem prompts start higher and use taller boxes, typically `x=0.224in, y=0.889in, w=9.39in`, with height adjusted to fit.
- Source PDF layout wins over the measured reference item grid when the two conflict. For source pages such as PDF page 10, where six fraction-conversion items appear as a single vertical list with answer parentheses aligned on the right, preserve that one-column row layout instead of using the reference two-column grid.
- For compact item grids, use two columns:
  - Left column starts around `x=0.25in`.
  - Right column starts around `x=5.30in`.
  - Common row baselines are near `y=2.35in`, `3.72in`, and `5.12in`.
- Problem number boxes are about `0.65in x 0.50in`; math text starts about `0.70in` to the right of the number.
- Answer blanks, circled locations, arrows, and rounded rectangles should be grouped with the item they complete.
- For vertical-list conversion exercises, place the problem number at the left, the stacked-fraction expression immediately to its right, and the answer parentheses in a consistent right-side column. Keep each item on one readable baseline; do not allow fractions, equals signs, decimal text, or answer parentheses to wrap into vertical fragments.
- Size stacked fractions from the source expression, not from a fixed small template. Use no-wrap numerator and denominator text boxes and a fraction bar at least wide enough for the longer of the numerator or denominator. For example, `19/10` must appear as `19` over `10` on one fraction bar, matching the PDF's readability.
- For problem-only slides, remove red source example answers from conversion rows. On PDF page 10, row (1) contains red filled answers in square blanks plus red `0.555...` and `무한소수`; the generated problem slide should keep the two empty square blanks and the answer parentheses, but not show the red answer text.
- Split subproblems across additional slides when the item count or formula height would force cramped spacing. Preserve the reference-style spacing rather than shrinking text excessively.
- When comparing a generated deck to the reference, evaluate only objects whose bounding boxes intersect the slide canvas. Ignore reference objects placed fully to the left, right, above, or below the slide, but do not leave those objects in the generated PPTX.

## Animation Pattern

- The reference deck uses no slide transitions.
- Reveals are implemented with `p:set` animation nodes that set `style.visibility` to `visible`.
- `p:set` targets are grouped shapes (`p:grpSp`). One reveal group usually corresponds to one answer, one completed item, one arrow, or one solution step.
- Keep the first example or first subproblem visible by default. Later subproblem groups appear in reading order on click.
- Each animated group should include the subproblem number, formula/text, answer blank or answer text, and any helper label/arrow/box that belongs to that item.
- Do not retarget reveal animations to loose text boxes. For example, reference slide 2 reveals grouped items in this order: target ids `13`, `7`, `12`, `5`, `4`; each target is a `p:grpSp` containing the problem number, expression, and answer blank. A generated slide whose `p:set` targets point at individual `p:sp` text boxes does not match the reference pattern, even if the animation XML still exists.
- Keep reveal order natural: left-to-right and top-to-bottom for grids; step order for worked examples.
- Preserve animations by copying or duplicating existing reference slides, then replacing text and images inside the duplicated slide.
- Avoid high-level PPTX writers for final animation-sensitive output if they rewrite or drop timing XML. If animation must be preserved, edit the PPTX package/XML while keeping `ppt/slides/slide*.xml` timing structures intact.
- After XML editing, verify every `p:spTgt @spid` exists on the slide and, for this measured style, every on-slide `p:set` reveal target resolves to a `p:grpSp`. If a duplicated template slide has timing targets for off-canvas helper objects, remove those helper objects and their timing nodes rather than preserving them in the generated deck.
- Sample reveal counts:
  - Slides 2, 3, 7, 9: 5 reveal groups.
  - Slides 4, 5, 10: 3 reveal groups.
  - Slides 11, 17: 2 reveal groups.
  - Slides 13, 14, 18, 19, 21: 1 reveal group.
  - Title slides and final static slides have no reveal animation.

## Blank Shape Pattern

- Do not type square blanks as literal `□` characters.
- Create square blank boxes only when the source PDF contains actual square blanks. If the PDF has no square blank, do not invent one.
- Reference square blanks are empty rounded-rectangle shapes (`a:prstGeom prst="roundRect"`) with a visible outline and solid fill, grouped with the surrounding item or step.
- Common blank-box sizes are about `0.63in x 0.47in`; variants include `0.47in x 0.47in`, `0.55in x 0.47in`, `0.71in x 0.47in`, and wider `1.06in x 0.47in` boxes when the answer needs more space.
- Blank boxes sit inline with the math/text they complete. Examples: slide 13 has two blank rounded rectangles; slide 14 has four; slide 17 has six; slide 21 has six.
- For rows like `1/7 = □ ÷ □ =`, the square blanks must be inline inside the formula row immediately after the matching symbols. Do not position these source blanks in the right answer column, at the far edge of the row, or after the final equals sign.
- For rows like `5/9 = [5] ÷ [9] = 0.555...`, where red numbers fill the source square blanks as an example answer, convert them to empty inline square blanks and hide the red decimal answer.
- Parenthesis blanks like `(    )` are plain text only in the O/X-style item grids where the reference uses parenthesis blanks. Use rounded-rectangle shapes for source problems that show square blanks.

## Construction Guidance

- Use these notes as measured style guidance, not as instructions to load a bundled template.
- Start from a user-provided reference PPTX only when the user explicitly supplies one for a non-deterministic conversion.
- Duplicate the closest matching slide type: title, two-column item grid, number-line/image item, transformation step, or long word-problem step.
- Replace text while preserving each shape's geometry, run-level fonts, and animation grouping.
- Before finalizing, compare the generated problem slide against the rendered source PDF block for row order, column count, answer-column alignment, and inline blank positions. Rebuild the slide if a source vertical list became a cramped two-column layout or if a square blank moved away from its formula anchor.
- For source math that extracts poorly, manually reconstruct formulas with `BT수식M`, baseline positioning, stacked fractions with horizontal fraction bars, small text boxes for numerators/denominators, and the same blank boxes/circles/arrows used in the reference deck.
- Do not use full-page PDF screenshots or cropped `개념 익히기` blocks as the main slide body unless the user explicitly requests image-only slides.
- Render or visually inspect the final PPTX before delivery. Check text overlap, clipping, visible page labels, and unnecessary square blank boxes; fix problems and provide only the corrected final deck.
- After generating a deck, run `../scripts/validate_editable_deck.py`. A deck like `.generated/pdf2concept-10-27/중등수학_2-1_10-27_개념익히기.pptx`, where problem slides are only large crop images, should be treated as failed output and rebuilt.
- Also run `../scripts/validate_reference_pattern.py --require-animations --require-group-animation --forbid-visible-page-labels --forbid-off-slide-objects`. Add `--require-blank-shapes` only when the generated problems include actual source PDF square blanks. On-slide square blanks typed as `□`, reveal targets that are loose text boxes, visible page labels, and any unrelated object outside the slide canvas should be treated as failed output and rebuilt.
