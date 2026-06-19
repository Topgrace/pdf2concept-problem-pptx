# Unit 1 Pages 10-19 Independent Style Map

Use this reference when generating the deterministic 10-19 deck for the verified middle-school math PDF. The runtime generator must not read `중2-1-1단원 개념익히기_참고용.pptx`; this file records the measured pattern from that human-made deck.

## Runtime Assets

The bundled runtime assets are in `../assets/unit1-10-19/`. The runtime generator must not read the reference PPTX, but it must use these measured assets and style parts so the output keeps the same theme, masters, layouts, and visible decorations.

- `title-character.png`: title-slide character decoration, displayed at `w=1.529in, h=1.578in`.
- `header-concept-practice-1.png`: concept-practice header for `개념 익히기 1`, displayed at `x=0.283in, y=0.528in, w=1.937in, h=0.463in`.
- `header-concept-practice-2.png`: concept-practice header for `개념 익히기 2`, displayed at `x=0.283in, y=0.528in, w=1.936in, h=0.464in`.
- `assets-manifest.json`: file size, pixel dimensions, and SHA-256 for the three PNG assets.
- `presentation-metadata.xml`: stripped `ppt/presentation.xml` metadata from the human-made deck, with embedded-font references removed. This supplies PowerPoint-compatible default text style and slide/master IDs without requiring runtime access to the reference PPTX.
- `ooxml-style-parts/`: extracted style-only OOXML from the human-made reference deck.
  - `ppt/theme/theme1.xml` and `ppt/theme/theme2.xml`.
  - `ppt/slideMasters/slideMaster1.xml`, `ppt/slideMasters/slideMaster2.xml`, and their `.rels`.
  - `ppt/slideLayouts/slideLayout1.xml` through `slideLayout4.xml` and their `.rels`.
  - `ppt/presProps.xml`, `ppt/viewProps.xml`, and `ppt/tableStyles.xml`.
  - `style-parts-manifest.json`: file size and SHA-256 for all embedded style parts.

## Fixed Slide Plan

- Slide 1: title, `01. 소수의 분류`, PDF concept page 10.
- Slides 2-3: PDF page 10, `개념 익히기 1`.
- Slides 4-5: PDF page 11, `개념 익히기 2`.
- Slide 6: title, `02. 유한소수로 나타낼 수 있는 분수`, PDF concept page 14.
- Slides 7-8: PDF page 14, `개념 익히기 1`.
- Slides 9-10: PDF page 15, `개념 익히기 2`.
- Slide 11: title, `03. 순환소수를 분수로 나타내기 (1)`, PDF concept page 18.
- Slide 12: PDF page 19, `개념 익히기 1`.

Exclude pages 12, 13, 16, and 17 because they are `개념 다지기` or `개념 마무리`. Exclude page 18 from problem slides because it is concept explanation only.

## Layout Constants

- Slide size: `13.333333in x 7.5in` (`12192000 x 6858000 EMU`).
- Title slides must follow the measured reference cover structure, not a centered fallback layout.
- Slide 1 title cover:
  - title text `소수의 분류`: `x=4.244in, y=2.788in, w=2.893in, h=0.774in`, `나눔스퀘어라운드 ExtraBold`, `sz=4000`;
  - back number `01`: `x=2.794in, y=2.527in, w=1.419in, h=1.279in`, `나눔스퀘어 ExtraBold`, `sz=7000`, fill `275184`, text outline `275184`, outline width `152400`;
  - front number `01`: same coordinates and font, fill `bg1`, no outline;
  - yellow `개념핵심` rounded rectangle: `x=2.458in, y=2.333in, w=0.716in, h=0.293in`, fill `F9EA5B`, no outline;
  - `개념핵심` text: `x=2.449in, y=2.341in, w=0.735in, h=0.278in`, `나눔스퀘어라운드 ExtraBold`, `sz=1050`, fill `275184`.
- Slide 6 title text: `02. 유한소수로 나타낼 수 있는 분수` at `x=2.477in, y=2.788in, w=8.380in, h=0.774in`, `sz=4000`.
- Slide 11 title text: `03.순환소수를 분수로 나타내기 (1)` at `x=2.871in, y=2.788in, w=8.343in, h=0.774in`, `sz=4000`.
- Title character image x-positions:
  - Slide 1: `x=9.143in`.
  - Slide 6: `x=11.592in`.
  - Slide 11: `x=11.343in`.
- Problem prompt starts at `x=0.224in, y=0.993in`; use `0.68in` height for short prompts and about `1.18in` for long prompts.
- Fonts:
  - Korean prompt/title/problem numbers: `나눔스퀘어라운드 ExtraBold`.
  - Cover slide large numbers: `나눔스퀘어 ExtraBold`.
  - Math formulas: `BT수식M`.
  - Default strict font preflight should fail when these fonts are not detected.
- Square blanks are rounded rectangles, not typed `□` characters.
- Fractions use stacked numerator/denominator text boxes with a horizontal fraction bar; numerator and denominator boxes must use no-wrap behavior.
- Recurring-decimal shorthand uses the single horizontal ellipsis character `…` (`U+2026`) from the reference deck, not three separate periods. Measured examples:
  - slide 4 item 1 text `0.7222…`: textbox `x=0.944in, y=2.734in, w=1.573in, h=0.505in`, run `sz=2400`;
  - slide 4 item 2 text `3.232323…`: textbox `x=0.944in, y=4.943in, w=1.927in, h=0.505in`, run `sz=2400`;
  - slide 12 item 1 text `42.36784784…`: textbox `x=0.899in, y=3.371in, w=2.458in, h=0.505in`, run `sz=2400`.
  Generated decimal continuations should normalize source `...` to `…` before writing visible math text so the ellipsis appears at the reference vertical height instead of the baseline.
- Page 10 `개념 익히기 1` stacked fractions must use one consistent math size across all subproblems. In particular, slide 3 items `(4) 1/7`, `(5) 19/10`, and `(6) 1/5` should all use the same numerator/denominator run size and textbox height; do not shrink `1/7` only because it appears in a blank-fill conversion formula.
- Page 10 `개념 익히기 1` conversion-row layout uses these measured slide 2 reference values:
  - problem number `(1)`: `x=0.254in, y=2.749in, w=0.652in, h=0.505in`, run `sz=2400`;
  - numerator `5`: `x=1.110in, y=2.683in, h=0.303in`, run `sz=2400`;
  - denominator `9`: `x=1.110in, y=3.037in, h=0.303in`, run `sz=2400`;
  - fraction bar: `x=1.021in, y=3.025in, w=0.355in, h=0`, line width `25400`;
  - relative to the problem-number textbox `y`, numerator top is about `-0.066in`, fraction bar about `+0.276in`, and denominator top about `+0.288in`;
  - inline blank boxes: `0.551in x 0.551in`, line width `31750`, positioned on the same row as the problem number;
  - answer parenthesis textbox: `x=6.227in, y=2.747in, w=2.762in, h=0.505in`, text equivalent to `(        )`, run `sz=2400`, no wrapping.
- Generated page 10 conversion rows should follow these ratios: fraction x offset about `+0.06in` from the formula anchor, numerator y offset about `-0.07in`, fraction bar about `+0.28in`, denominator about `+0.29in`, square blank size about `0.551in`, square blank line width `31750`, and answer parentheses as one no-wrap text box in a wide right answer column.
- Exponents are superscript text runs, never visible caret notation. For example, render `2^2` as base `2` with a smaller raised `2`, not the literal text `2^2`.
- Page 15 factorization fractions use the measured reference exponent style. In `중2-1-1단원 개념익히기_참고용.pptx` slide 9 item 1:
  - denominator textbox `22\3\5`: `x=1.115in, y=3.383in, w=1.339in, h=0.404in`;
  - denominator runs: base `2` at `sz=2400, baseline=0`, exponent `2` at `sz=2000, baseline=60000`, remaining `\3\5` at `sz=2400, baseline=0`;
  - numerator `7`: `x=1.696in, y=2.935in, w=0.177in, h=0.404in`;
  - fraction bar: `x=1.076in, y=3.355in, w=1.417in, h=0`;
  - relative to the problem number textbox `y=3.371in`, the bar is about `-0.016in`, numerator about `-0.436in`, and denominator about `+0.012in`.
- Page 15 `개념 익히기 2` grid layout must use the measured reference row/column positions so subproblems and answer parentheses do not collide with each other or move into the blue side background:
  - top-left item number: `x=0.246in, y=3.371in`; formula anchor/fraction bar starts near `x=1.076in`; answer parenthesis `x=3.061in, y=3.246in, w=1.285in, h=0.649in`;
  - top-right item number: `x=5.423in, y=3.371in`; formula anchor/fraction bar starts near `x=6.285in`; answer parenthesis `x=8.238in, y=3.246in, w=1.285in, h=0.649in`;
  - bottom-left item number: `x=0.246in, y=5.246in`; formula anchor/fraction bar starts near `x=1.357in`; answer parenthesis `x=3.061in, y=5.120in, w=1.285in, h=0.649in`;
  - bottom-right item number: `x=5.423in, y=5.246in`; formula anchor/fraction bar starts near `x=6.285in`; answer parenthesis `x=8.238in, y=5.120in, w=1.285in, h=0.649in`.
  Do not use the earlier fallback grid row anchors `y=2.55in` and `y=4.35in`; they place the page 15 subproblems too high and make the row spacing diverge from the reference.
- Generated page 15-style fractions should follow those ratios: use about 24pt math text for denominator/base, about 20pt for exponent, `baseline=60000`, a wide fraction bar, and a denominator textbox just below the bar. Do not render the exponent as a separate low textbox beside the base.
- PDF page 14 `개념 익히기 1` keeps source denominator blanks:
  - Slide 7 item 1: `3/(__^2×__)`, two rounded-rectangle blanks in the denominator; hide the red answer factors `2, 5`.
  - Slide 7 item 2: `11/(__^2×__^2)`, four denominator components: blank, exponent `2`, multiplication sign, blank, exponent `2`.
  - Slide 8 item 3: `2/__`; slide 8 item 4: `1/(__^3)`; slide 8 item 5: `8/__`.
  - The exponent is a small separate raised text object positioned immediately to the upper-right of the blank box, not caret text and not centered as a normal denominator digit.
- Page 14 chained-equality fractions must align the fraction bar with the adjacent equals-sign centerline, not with the page 15 factorization denominator pattern. In the human-made reference deck slide 7 item 1:
  - problem number `(1)`: `x=0.256in, y=2.757in, w=0.652in, h=0.505in`, run `sz=2400`;
  - inline text `0.15=`: `x=0.895in, y=2.721in, w=1.219in, h=0.505in`, run `sz=2400`;
  - numerator `15`: `x=2.208in, y=2.566in, h=0.404in`; denominator `100`: `x=2.119in, y=2.960in, h=0.404in`; fraction bar `x=2.070in, y=2.985in, w=0.630in`, line width `25400`;
  - numerator `3`: `x=3.729in, y=2.566in, h=0.404in`; denominator `20`: `x=3.633in, y=2.960in, h=0.404in`; fraction bar `x=3.582in, y=2.985in, w=0.472in`, line width `25400`;
  - denominator-blank fraction numerator `3`: `x=4.976in, y=2.566in, h=0.404in`; fraction bar `x=4.125in, y=2.985in, w=1.811in`; blank boxes at `y=3.074in`, `0.551in x 0.551in`, line width `31750`.
- Generated page 14 chained-equality rows should follow these offsets relative to the formula row anchor: numerator y about `-0.19in`, fraction bar about `+0.24in`, denominator text about `+0.20in`, and denominator blank-pattern base about `+0.26in`. These offsets keep the bar on the equals line and keep blanks under the bar like the reference.

## Animation Pattern

- The first item on each problem slide is visible by default.
- Every later item is wrapped in one `p:grpSp` and revealed in reading order with a `p:set` animation targeting that group.
- Timing target groups include problem number, expression/fraction/blank shapes, answer parentheses, and helper text for that item.
- Generated slides must not contain page labels or any object outside the slide canvas.

## Deterministic Generator

Run `../scripts/generate_unit1_10_19.py` for this exact case:

```bash
python ../scripts/generate_unit1_10_19.py --pdf <input.pdf> --output <output.pptx> --report <report.json>
```

The generator verifies the input PDF size and SHA-256, writes a 12-slide editable PPTX directly as OOXML, embeds the three bundled PNG assets plus bundled presentation metadata and style OOXML parts, and records `runtime_reference_pptx_used: false` in the report. A valid output must open in Microsoft PowerPoint and export slides 7 and 8 to PNG without repair prompts or corruption errors.
