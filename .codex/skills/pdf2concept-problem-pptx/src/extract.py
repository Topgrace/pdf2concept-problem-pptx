from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import fitz

from .ir import PracticeBlock, PracticeItem, SourceBox, infer_layout_type


@dataclass
class PositionedLine:
    text: str
    box: SourceBox


FRACTION_NUMERATOR_GLYPHS = {
    "!": "1",
    "Á": "1",
    "ª": "2",
    "#": "3",
    "£": "3",
    "¢": "4",
}

FRACTION_DENOMINATOR_GLYPHS = {
    "[": "x",
    "]": "y",
}

MATH_FACTOR = r"-?[0-9A-Za-z가-힣⁰¹²³⁴⁵⁶⁷⁸⁹]+"
MATH_SUM = rf"{MATH_FACTOR}(?:[+\-×]{MATH_FACTOR})+"
MULTIPLICATION_CHAIN = rf"{MATH_FACTOR}(?:×{MATH_FACTOR})+"

EXPLANATORY_TAIL_MARKERS = (
    "곱셈으로 바꾸거나",
    "분수 꼴로 바꾸거나",
    "단항식의 곱셈",
    "단항식의 나눗셈",
    "나눗셈을 곱셈",
    "약분이 되면",
    "거듭제곱이 있으면",
    "다음을 계산하시오",
    "세로셈도",
    "다항식의 덧셈",
    "다항식의 뺄셈",
    "뺄셈은 부호",
    "4x 4x",
)

EXPECTED_UNIT1_PDF_SHA256 = "746e6d7fa48c826df0c83aa3f2f59424cb0ffa6076ed481e9a9c89c5fbf5baaf"

UNIT1_10_19_BLOCKS = [
    PracticeBlock(
        page=10,
        concept_no="01",
        concept_title="소수의 분류",
        practice_no="1",
        prompt="다음 분수를 소수로 바꾸어 보고, 유한소수인지 무한소수인지 구분하시오.",
        items=[
            "(1) 5/9 = [ ] ÷ [ ] = (        )",
            "(2) 3/4 = 3 ÷ 4 = (        )",
            "(3) 1/6 = 1 ÷ 6 = (        )",
            "(4) 1/7 = [ ] ÷ [ ] = (        )",
            "(5) 19/10 = (        )",
            "(6) 1/5 = (        )",
        ],
        layout_type="vertical_list",
    ),
    PracticeBlock(
        page=11,
        concept_no="01",
        concept_title="소수의 분류",
        practice_no="2",
        prompt="다음 순환소수의 순환마디를 쓰고, 순환마디에 점을 찍어 간단히 나타내시오.",
        item_models=[
            PracticeItem.from_text(
                "(1) 0.7222…  순환마디:        간단히 표현:",
                row_index=0,
                source_lines=["(1) 0.7222…", "순환마디:", "간단히 표현:"],
            ),
            PracticeItem.from_text(
                "(2) 3.232323…  순환마디:        간단히 표현:",
                row_index=1,
                source_lines=["(2) 3.232323…", "순환마디:", "간단히 표현:"],
            ),
            PracticeItem.from_text(
                "(3) 9.78777…  순환마디:        간단히 표현:",
                row_index=2,
                source_lines=["(3) 9.78777…", "순환마디:", "간단히 표현:"],
            ),
            PracticeItem.from_text(
                "(4) 560.505050…  순환마디:        간단히 표현:",
                row_index=3,
                source_lines=["(4) 560.505050…", "순환마디:", "간단히 표현:"],
            ),
        ],
        layout_type="vertical_list",
    ),
    PracticeBlock(
        page=14,
        concept_no="02",
        concept_title="유한소수로 나타낼 수 있는 분수",
        practice_no="1",
        prompt="다음은 유한소수를 분수로 바꾼 것이다. 분모를 소인수분해 하고, 분모의 소인수를 모두 구하시오.",
        items=[
            "(1) 0.15 = 15/100 = 3/20 = 3/([ ]²×[ ])    분모의 소인수:",
            "(2) 0.11 = 11/100 = 11/([ ]²×[ ]²)    분모의 소인수:",
            "(3) 0.4 = 4/10 = 2/[ ]    분모의 소인수:",
            "(4) 0.125 = 125/1000 = 1/8 = 1/([ ]³)    분모의 소인수:",
            "(5) 1.6 = 16/10 = 8/[ ]    분모의 소인수:",
        ],
        layout_type="worked_stack",
    ),
    PracticeBlock(
        page=15,
        concept_no="02",
        concept_title="유한소수로 나타낼 수 있는 분수",
        practice_no="2",
        prompt="다음은 기약분수의 분모를 소인수분해 한 것이다. 다음 분수를 유한소수로 나타낼 수 있으면 '유', 순환소수로 나타낼 수 있으면 '순'이라고 쓰시오.",
        items=[
            "(1) 7/(2²×3×5)     (          )",
            "(2) 2/(3²×5)     (          )",
            "(3) 1/13     (          )",
            "(4) 1/(2×5)     (          )",
            "(5) 11/(2×5)     (          )",
            "(6) 5²/(2×7)     (          )",
            "(7) 7/(2³×5³)     (          )",
            "(8) 2⁵/(5²×13)     (          )",
        ],
        layout_type="two_column_grid",
    ),
    PracticeBlock(
        page=19,
        concept_no="03",
        concept_title="순환소수를 분수로 나타내기 (1)",
        practice_no="1",
        prompt="주어진 순환소수에서 처음 등장하는 순환마디에 ○표 하고, 그 순환마디의 앞과 뒤에 소수점이 놓이도록 화살표를 그리시오. (소수점이 이미 순환마디 앞에 있는 경우는 화살표를 하나만 그리기)",
        items=[
            "(1) 42.36784784…",
            "(2) 0.3555…",
            "(3) 0.666…",
            "(4) 1.252525…",
        ],
        layout_type="vertical_list",
    ),
]

UNIT1_10_19_EXCLUDED = {
    "12": "개념 다지기",
    "13": "개념 마무리",
    "16": "개념 다지기",
    "17": "개념 마무리",
    "18": "개념핵심 설명 페이지이며 개념익히기 문제 없음",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_page_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*[-~]\s*(\d+)\s*", value)
    if not match:
        raise SystemExit("--pages must look like 10-19 or 10~19")
    start, end = int(match.group(1)), int(match.group(2))
    if start <= 0 or end < start:
        raise SystemExit(f"Invalid page range: {value}")
    return start, end


def decode_semicolon_fraction(match: re.Match[str]) -> str:
    token = match.group(1).replace("~", "")
    numerator_pos = -1
    numerator = ""
    for idx, char in enumerate(token):
        if char in FRACTION_NUMERATOR_GLYPHS:
            numerator_pos = idx
            numerator = FRACTION_NUMERATOR_GLYPHS[char]
            break
    if numerator_pos < 0:
        return match.group(0)

    denominator = token[:numerator_pos] + token[numerator_pos + 1 :]
    for old, new in FRACTION_DENOMINATOR_GLYPHS.items():
        denominator = denominator.replace(old, new)
    denominator = denominator.strip()
    if not denominator:
        return match.group(0)
    return f"{numerator}/{denominator}"


def normalize_encoded_fractions(text: str) -> str:
    return re.sub(r";([^;]+);", decode_semicolon_fraction, text)


def normalize_math_text(text: str) -> str:
    text = normalize_encoded_fractions(text)
    replacements = {
        "Ú`â`": "¹⁰",
        "Ú`Û`": "¹²",
        "Ú`Þ`": "¹⁵",
        "Ú`ß`": "¹⁶",
        "Ú`": "¹",
        "Û`": "²",
        "Ü`": "³",
        "Ý`": "⁴",
        "Þ`": "⁵",
        "ß`": "⁶",
        "à`": "⁷",
        "á`": "⁸",
        "¡`": "⁹",
        "º`": "⁰",
        "Û": "²",
        "Ü": "³",
        "Ý": "⁴",
        "Þ": "⁵",
        "ß": "⁶",
        "à": "⁷",
        "á": "⁸",
        "¡": "⁹",
        "º": "⁰",
        "_": "×",
        "Ö": "÷",
        "`": "",
        "\a": "",
        "...": "…",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("× ×", "×")
    return text.strip()


def clean_line(line: str) -> str:
    line = normalize_math_text(line.strip())
    line = re.sub(r"^\s*▶\s*", "", line)
    return line.strip()


def is_explanatory_tail(line: str) -> bool:
    return any(marker in line for marker in EXPLANATORY_TAIL_MARKERS)


def trim_explanatory_tail(text: str) -> str:
    cut_at = len(text)
    for marker in EXPLANATORY_TAIL_MARKERS:
        marker_index = text.find(marker)
        if marker_index > 0:
            cut_at = min(cut_at, marker_index)
    return text[:cut_at].strip()


def repair_leading_stacked_fraction(text: str) -> str:
    """Convert PDF text-order numerator/denominator lines into slash fractions.

    PyMuPDF often returns stacked expressions as "numerator denominator" when
    the denominator is drawn on a separate baseline. We normalize that compact
    form here so the PPTX math renderer can rebuild an editable horizontal
    fraction bar later.
    """

    target_pattern = re.compile(
        rf"^(\(\d+\)\s+)({MATH_SUM})\s+({MATH_FACTOR})(\s+\[\s*\d+\s*\])"
    )
    text = target_pattern.sub(r"\1(\2)/\3\4", text, count=1)

    worked_pattern = re.compile(
        rf"^(\(\d+\)\s+)({MATH_SUM})\s+({MATH_FACTOR})(\s+\[\s*\])?(?=\s*=)"
    )

    def replace_worked(match: re.Match[str]) -> str:
        denominator = match.group(3)
        blank = match.group(4) or ""
        if not blank and f"1/{denominator}" not in text and f"/{denominator}" not in text:
            return match.group(0)
        return f"{match.group(1)}({match.group(2)})/{denominator}{blank}"

    return worked_pattern.sub(replace_worked, text, count=1)


def repair_reciprocal_blanks(text: str) -> str:
    text = re.sub(r"×\s+1\s+\[\s*\]", "×1/[ ]", text)
    text = re.sub(r"=\s+1\s+\[\s*\]", "=1/[ ]", text)
    return text


def repair_quotient_expansion_stacks(text: str) -> str:
    text = re.sub(
        rf"×\s+1\s+({MULTIPLICATION_CHAIN})(?=\s*=)",
        r"×1/(\1)",
        text,
    )
    text = re.sub(
        rf"×1/\[\s*\]\s+({MULTIPLICATION_CHAIN})(?=\s*=)",
        r"×1/(\1)",
        text,
    )
    text = re.sub(
        rf"=\s*1/\[\s*\]\s+({MATH_FACTOR}\s+\[\s*\])\s*$",
        r"=1/(\1)",
        text,
    )
    return text


def repair_vertical_polynomial_stack(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    replacements = {
        r"^\((?P<number>\d+)\)\s+9a\+\s*b-8\s+\+>²\s+a\+4b-2$": r"(\g<number>) 9a+b-8+(a+4b-2)",
        r"^\((?P<number>\d+)\)\s+5a-\s*b\+6\s+->²\s+3a\+10b\+2$": r"(\g<number>) 5a-b+6-(3a+10b+2)",
    }
    for pattern, replacement in replacements.items():
        compact = re.sub(pattern, replacement, compact)
    return compact


def repair_division_worked_fraction_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()

    match = re.match(
        rf"^(\(\d+\)\s+)\((?P<body>{MATH_SUM})\)÷(?P<den>{MATH_FACTOR})\s*=\s*(?P=den)\s*=\s*(?P<n1>{MATH_FACTOR})\s+(?P=den)\s*-\s*(?P<n2>{MATH_FACTOR})\s+(?P=den)\s*=$",
        compact,
    )
    if match:
        prefix = match.group(1)
        body = match.group("body")
        denominator = match.group("den")
        return (
            f"{prefix}({body})÷{denominator}"
            f"=({body})×1/{denominator}"
            f"={match.group('n1')}/{denominator}-{match.group('n2')}/{denominator}="
        )

    match = re.match(
        rf"^(\(\d+\)\s+)\((?P<body>{MATH_SUM})\)÷(?P<den>{MATH_FACTOR})\s*=\s*=\s*(?P<n1>{MATH_FACTOR})\s+(?P=den)\s*\+\s*(?P<n2>{MATH_FACTOR})\s+(?P=den)\s*=$",
        compact,
    )
    if match:
        prefix = match.group(1)
        body = match.group("body")
        denominator = match.group("den")
        return (
            f"{prefix}({body})÷{denominator}"
            f"=({body})×1/{denominator}"
            f"={match.group('n1')}/{denominator}+{match.group('n2')}/{denominator}="
        )

    match = re.match(
        rf"^(\(\d+\)\s+)\((?P<body>{MATH_SUM})\)÷(?P<divisor>{MATH_FACTOR}/{MATH_FACTOR})\s*=\((?P=body)\)×\s*=(?P<tail>.+)$",
        compact,
    )
    if match:
        reciprocal_match = re.search(rf"×\s*({MATH_FACTOR}/{MATH_FACTOR})", match.group("tail"))
        reciprocal = reciprocal_match.group(1) if reciprocal_match else reciprocal_fraction(match.group("divisor"))
        return (
            f"{match.group(1)}({match.group('body')})÷{match.group('divisor')}"
            f"=({match.group('body')})×{reciprocal}={match.group('tail')}"
        )

    return text


def reciprocal_fraction(value: str) -> str:
    numerator, denominator = value.split("/", 1)
    return f"{denominator}/{numerator}"


def repair_extracted_item_text(text: str) -> str:
    text = trim_explanatory_tail(text)
    text = repair_leading_stacked_fraction(text)
    text = repair_reciprocal_blanks(text)
    text = repair_quotient_expansion_stacks(text)
    text = repair_vertical_polynomial_stack(text)
    text = repair_division_worked_fraction_text(text)
    if "÷" not in text:
        return text

    text = re.sub(
        rf"×\s+1\s+({MATH_FACTOR})(?=\s*=)",
        r"×1/\1",
        text,
    )
    text = re.sub(
        rf"×\s+({MATH_FACTOR})(?=\s*=)",
        r"×1/\1",
        text,
    )
    text = re.sub(
        rf"=\s+({MATH_FACTOR})\s+({MATH_FACTOR})\s*=",
        r"=\1/\2=",
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    noise_patterns = [
        r"^●\s*정답",
        r"^동영상 강의",
        r"^중\s*2학년",
        r"^Ⅱ\.",
        r"^2-\d+",
        r"^개념핵심$",
        r"^개념\s*핵심$",
        r"^주의할 점$",
    ]
    return any(re.search(pattern, line) for pattern in noise_patterns)


def is_footer_or_page_number(line: PositionedLine, page_rect) -> bool:
    text = line.text.strip()
    if not re.fullmatch(r"\d+", text):
        return False
    return line.box.y0 > page_rect.height - 35 or line.box.x0 > page_rect.width - 60


def should_append_item_continuation(item_start: PositionedLine, candidate: PositionedLine, page_rect) -> bool:
    if is_footer_or_page_number(candidate, page_rect):
        return False
    if re.fullmatch(r"\d+", candidate.text.strip()):
        horizontally_related = item_start.box.x0 - 12 <= candidate.box.x0 <= item_start.box.x1 + 120
        vertically_related = candidate.box.y0 <= item_start.box.y1 + 90
        return horizontally_related and vertically_related
    return True


def item_number(line: str) -> int | None:
    circled = "⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿"
    if line and line[0] in circled:
        return circled.index(line[0]) + 1
    match = re.match(r"^\((\d{1,2})\)", line)
    if match:
        return int(match.group(1))
    return None


def normalize_item_number(line: str) -> str:
    circled = "⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿"
    if line and line[0] in circled:
        return f"({circled.index(line[0]) + 1}) {line[1:].strip()}"
    return line


def is_red_answer_color(color: int | None) -> bool:
    if color is None:
        return False
    red = (color >> 16) & 0xFF
    green = (color >> 8) & 0xFF
    blue = color & 0xFF
    return red >= 180 and green <= 80 and blue <= 100


def detect_blank_rects(page) -> list[SourceBox]:
    blanks: list[SourceBox] = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if not rect:
            continue
        x0, y0, x1, y1 = rect
        width = x1 - x0
        height = y1 - y0
        color = drawing.get("color")
        fill = drawing.get("fill")
        is_gray_line = bool(color) and all(0.35 <= channel <= 0.65 for channel in color)
        if (
            8 <= width <= 70
            and 8 <= height <= 28
            and y0 >= 430
            and is_gray_line
            and fill is None
        ):
            blanks.append(SourceBox(x0=x0, y0=y0, x1=x1, y1=y1))
    return blanks


def blank_belongs_to_line(blank: SourceBox, line: SourceBox) -> bool:
    blank_center_y = (blank.y0 + blank.y1) / 2
    vertically_aligned = line.y0 - 2 <= blank_center_y <= line.y1 + 2
    horizontally_near = blank.x0 <= line.x1 + 35 and blank.x1 >= line.x0 - 6
    return vertically_aligned and horizontally_near


def blank_contains_span(blank: SourceBox, span: SourceBox) -> bool:
    center_x = (span.x0 + span.x1) / 2
    center_y = (span.y0 + span.y1) / 2
    return blank.x0 - 2 <= center_x <= blank.x1 + 2 and blank.y0 - 3 <= center_y <= blank.y1 + 3


def extract_positioned_lines(page) -> list[PositionedLine]:
    positioned: list[PositionedLine] = []
    blank_rects = detect_blank_rects(page)
    page_dict = page.get_text("dict")
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            line_box = SourceBox(*line.get("bbox", (0, 0, 0, 0)))
            used_blank_indexes: set[int] = set()
            tokens: list[tuple[float, str]] = []
            for span in spans:
                span_text = span.get("text", "")
                if not span_text:
                    continue
                span_box = SourceBox(*span.get("bbox", (0, 0, 0, 0)))
                if is_red_answer_color(span.get("color")):
                    for idx, blank in enumerate(blank_rects):
                        if idx in used_blank_indexes:
                            continue
                        if blank_contains_span(blank, span_box):
                            tokens.append((blank.x0, " [ ] "))
                            used_blank_indexes.add(idx)
                            break
                    continue
                tokens.append((span_box.x0, span_text))

            for idx, blank in enumerate(blank_rects):
                if idx in used_blank_indexes:
                    continue
                if blank_belongs_to_line(blank, line_box):
                    tokens.append((blank.x0, " [ ] "))

            text = clean_line("".join(token for _, token in sorted(tokens, key=lambda item: item[0])))
            if not text:
                continue
            x0, y0, x1, y1 = line.get("bbox", (0, 0, 0, 0))
            positioned.append(PositionedLine(text=text, box=SourceBox(x0=x0, y0=y0, x1=x1, y1=y1)))
    return positioned


def match_item_boxes(positioned_lines: list[PositionedLine]) -> dict[int, SourceBox]:
    boxes: dict[int, SourceBox] = {}
    for line in positioned_lines:
        no = item_number(normalize_item_number(line.text))
        if no is not None and no not in boxes:
            boxes[no] = line.box
    return boxes


def build_item_models(
    items: list[str],
    boxes: dict[int, SourceBox],
    page_width: float,
    source_lines_by_number: dict[int, list[str]] | None = None,
) -> list[PracticeItem]:
    models: list[PracticeItem] = []
    row_index_by_column = {0: 0, 1: 0}
    source_lines_by_number = source_lines_by_number or {}
    for fallback_row, item in enumerate(items):
        no = item_number(item)
        box = boxes.get(no) if no is not None else None
        column_index = 0
        if box and box.center_x > page_width * 0.52:
            column_index = 1
        row_index = row_index_by_column[column_index] if box else fallback_row
        row_index_by_column[column_index] += 1
        models.append(
            PracticeItem.from_text(
                item,
                row_index=row_index,
                column_index=column_index,
                source_box=box,
                source_lines=source_lines_by_number.get(no or -1, [item]),
            )
        )
    return models


def likely_prompt(lines: list[str]) -> str:
    prompt_candidates = []
    prompt_markers = (
        "빈칸",
        "다음",
        "계산",
        "구하시오",
        "쓰시오",
        "이으시오",
        "나타내시오",
        "채우시오",
        "표 하고",
    )
    for line in lines:
        if is_noise_line(line):
            continue
        if any(marker in line for marker in prompt_markers) and len(line) >= 8:
            prompt_candidates.append(line)
    if prompt_candidates:
        return prompt_candidates[-1]
    return "다음 문제를 해결하시오."


def concept_from_page(lines: list[str], fallback_no: str, fallback_title: str) -> tuple[str, str]:
    concept_no = fallback_no
    concept_title = fallback_title
    for idx, line in enumerate(lines):
        if re.fullmatch(r"\d{2}\.", line):
            concept_no = line[:2]
            for prev in reversed(lines[max(0, idx - 6) : idx]):
                if (
                    prev
                    and not is_noise_line(prev)
                    and not re.search(r"개념|핵심|배울 내용|정답|해설", prev)
                    and len(prev) <= 28
                ):
                    concept_title = prev
                    break
            break
    return concept_no, concept_title


def extract_practice_blocks(pdf_path: Path, start_page: int, end_page: int) -> tuple[list[PracticeBlock], dict]:
    doc = fitz.open(pdf_path)
    if end_page > doc.page_count:
        raise SystemExit(f"Requested page {end_page}, but PDF has only {doc.page_count} pages.")

    blocks: list[PracticeBlock] = []
    excluded: dict[str, str] = {}
    current_no = ""
    current_title = "개념 익히기"

    for page_no in range(start_page, end_page + 1):
        page = doc[page_no - 1]
        positioned_lines = extract_positioned_lines(page)
        item_boxes = match_item_boxes(positioned_lines)
        content_lines = [
            line
            for line in positioned_lines
            if line.text and not is_noise_line(line.text) and not is_footer_or_page_number(line, page.rect)
        ]
        lines = [line.text for line in content_lines]
        joined = "\n".join(lines)
        current_no, current_title = concept_from_page(lines, current_no, current_title)

        practice_matches = list(re.finditer(r"개념\s*익히기\s*(\d+)?", joined))
        if not practice_matches:
            reason = "개념익히기 없음"
            if "개념 다지기" in joined:
                reason = "개념 다지기"
            elif "개념 마무리" in joined:
                reason = "개념 마무리"
            elif "학교 시험 준비하기" in joined:
                reason = "학교 시험 준비하기"
            excluded[str(page_no)] = reason
            continue

        practice_no = practice_matches[0].group(1) or "1"
        item_lines: list[tuple[str, list[str]]] = []
        for idx, positioned_line in enumerate(content_lines):
            line = positioned_line.text
            if item_number(line) is not None:
                combined = normalize_item_number(line)
                combined_source_lines = [combined]
                lookahead = idx + 1
                while lookahead < len(content_lines):
                    nxt_line = content_lines[lookahead]
                    nxt = nxt_line.text
                    if item_number(nxt) is not None or "개념 익히기" in nxt or "개념익히기" in nxt:
                        break
                    if not should_append_item_continuation(positioned_line, nxt_line, page.rect):
                        break
                    if is_explanatory_tail(nxt):
                        break
                    if any(marker in nxt for marker in ("정답", "해설", "동영상", "개념 다지기", "개념 마무리")):
                        break
                    if len(combined) < 95 and len(nxt) <= 35 and not re.fullmatch(r"[①-⑤ㄱ-ㅎ]+", nxt):
                        combined += " " + nxt
                        combined_source_lines.append(nxt)
                        lookahead += 1
                        continue
                    break
                item_lines.append((combined, combined_source_lines))

        unique_items = []
        source_lines_by_number: dict[int, list[str]] = {}
        seen_numbers: set[int] = set()
        for item, source_lines in item_lines:
            item = repair_extracted_item_text(item)
            no = item_number(item)
            if no is None or no in seen_numbers:
                continue
            seen_numbers.add(no)
            unique_items.append(item)
            source_lines_by_number[no] = source_lines

        if not unique_items:
            excluded[str(page_no)] = "개념익히기 텍스트 항목 추출 실패"
            continue

        item_models = build_item_models(unique_items, item_boxes, page.rect.width, source_lines_by_number)
        layout_type = infer_layout_type(item_models)
        blocks.append(
            PracticeBlock(
                page=page_no,
                concept_no=current_no,
                concept_title=current_title,
                practice_no=practice_no,
                prompt=likely_prompt(lines),
                items=unique_items,
                item_models=item_models,
                layout_type=layout_type,
                source_lines=lines,
            )
        )
    return blocks, excluded
