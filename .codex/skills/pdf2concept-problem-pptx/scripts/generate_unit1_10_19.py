#!/usr/bin/env python3
"""Generate the unit 1 pages 10-19 concept-practice deck without a PPTX template.

This deterministic generator encodes the measured layout pattern from the
human-made unit 1 reference deck. At runtime it only depends on the input PDF
and image assets bundled inside this skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSET_DIR = SKILL_DIR / "assets" / "unit1-10-19"
STYLE_PARTS_DIR = ASSET_DIR / "ooxml-style-parts"
PRESENTATION_METADATA = ASSET_DIR / "presentation-metadata.xml"
EMU = 914400
SLIDE_W_IN = 13.333333
SLIDE_H_IN = 7.5
SLIDE_W_EMU = 12192000
SLIDE_H_EMU = 6858000
REFERENCE_SUPERSCRIPT_BASELINE = 60000
REFERENCE_SUPERSCRIPT_SIZE_RATIO = 20 / 24
INLINE_FRACTION_NUMERATOR_Y_OFFSET = -0.44
INLINE_FRACTION_BAR_Y_OFFSET = -0.02
INLINE_FRACTION_DENOMINATOR_Y_OFFSET = 0.01
PAGE10_FRACTION_X_OFFSET = 0.06
PAGE10_FRACTION_NUMERATOR_Y_OFFSET = -0.07
PAGE10_FRACTION_BAR_Y_OFFSET = 0.28
PAGE10_FRACTION_DENOMINATOR_Y_OFFSET = 0.29
PAGE10_FRACTION_MIN_WIDTH = 0.42
PAGE14_FRACTION_NUMERATOR_Y_OFFSET = -0.19
PAGE14_FRACTION_BAR_Y_OFFSET = 0.24
PAGE14_FRACTION_DENOMINATOR_Y_OFFSET = 0.20
PAGE14_FRACTION_PATTERN_Y_OFFSET = 0.26
PAGE14_FRACTION_MIN_WIDTH = 0.55
REFERENCE_BLANK_BOX_SIZE = 0.551
REFERENCE_BLANK_LINE_WIDTH = "31750"
REFERENCE_DECIMAL_ELLIPSIS = "\u2026"

EXPECTED_PDF_SHA256 = "746e6d7fa48c826df0c83aa3f2f59424cb0ffa6076ed481e9a9c89c5fbf5baaf"
EXPECTED_PDF_SIZE = 13178070
PRESENTATION_METADATA_SHA256 = "b54acc2dea1403e19210ffdc4278cbc99aa442c13d667532b12c06a649a651f8"
REQUIRED_FONTS = ("나눔스퀘어라운드 ExtraBold", "BT수식M")
STYLE_PART_CONTENT_TYPES = {
    "ppt/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
    "ppt/theme/theme2.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
    "ppt/slideMasters/slideMaster1.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml",
    "ppt/slideMasters/slideMaster2.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml",
    "ppt/slideLayouts/slideLayout1.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml",
    "ppt/slideLayouts/slideLayout2.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml",
    "ppt/slideLayouts/slideLayout3.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml",
    "ppt/slideLayouts/slideLayout4.xml": "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml",
    "ppt/presProps.xml": "application/vnd.openxmlformats-officedocument.presentationml.presProps+xml",
    "ppt/viewProps.xml": "application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml",
    "ppt/tableStyles.xml": "application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml",
}

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
}

for prefix, uri in NS.items():
    if prefix not in {"rel", "ct"}:
        etree.register_namespace(prefix, uri)


SLIDE_PLAN = [
    {"kind": "title", "title": "소수의 분류", "number": "01", "image_x": 9.143},
    {
        "kind": "problem",
        "header": "header-concept-practice-1.png",
        "prompt": "다음 분수를 소수로 바꾸어 보고, 유한소수인지 무한소수인지 구분하시오.",
        "layout": "page10_a",
        "items": [
            {"no": "(1)", "expr": "5/9 = __ ÷ __ =", "ans": "(        )", "blank_formula": True},
            {"no": "(2)", "expr": "3/4 = 3 ÷ 4 =", "ans": "(        )"},
            {"no": "(3)", "expr": "1/6 = 1 ÷ 6 =", "ans": "(        )"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-1.png",
        "prompt": "다음 분수를 소수로 바꾸어 보고, 유한소수인지 무한소수인지 구분하시오.",
        "layout": "page10_b",
        "items": [
            {"no": "(4)", "expr": "1/7 = __ ÷ __ =", "ans": "(        )", "blank_formula": True},
            {"no": "(5)", "expr": "19/10 =", "ans": "(        )"},
            {"no": "(6)", "expr": "1/5 =", "ans": "(        )"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-2.png",
        "prompt": "다음 순환소수의 순환마디를 쓰고, 순환마디에 점을 찍어 간단히 나타내시오.",
        "layout": "tworow",
        "items": [
            {"no": "(1)", "expr": "0.7222...", "ans": "순환마디:\n간단히 표현:"},
            {"no": "(2)", "expr": "3.232323...", "ans": "순환마디:\n간단히 표현:"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-2.png",
        "prompt": "다음 순환소수의 순환마디를 쓰고, 순환마디에 점을 찍어 간단히 나타내시오.",
        "layout": "tworow",
        "items": [
            {"no": "(3)", "expr": "9.78777...", "ans": "순환마디:\n간단히 표현:"},
            {"no": "(4)", "expr": "560.505050...", "ans": "순환마디:\n간단히 표현:"},
        ],
    },
    {"kind": "title", "title": "유한소수로 나타낼 수 있는 분수", "number": "02", "image_x": 11.592},
    {
        "kind": "problem",
        "header": "header-concept-practice-1.png",
        "prompt": "다음은 유한소수를 분수로 바꾼 것이다. 분모를 소인수분해 하고, 분모의 소인수를 모두 구하시오.",
        "layout": "page14_a",
        "items": [
            {"no": "(1)", "expr": "0.15 = 15/100 = 3/20 = 3/(__^2×__)", "ans": "분모의 소인수:"},
            {"no": "(2)", "expr": "0.11 = 11/100 = 11/(__^2×__^2)", "ans": "분모의 소인수:"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-1.png",
        "prompt": "다음은 유한소수를 분수로 바꾼 것이다. 분모를 소인수분해 하고, 분모의 소인수를 모두 구하시오.",
        "layout": "page14_b",
        "items": [
            {"no": "(3)", "expr": "0.4 = 4/10 = 2/__", "ans": "분모의 소인수:"},
            {"no": "(4)", "expr": "0.125 = 125/1000 = 1/8 = 1/(__^3)", "ans": "분모의 소인수:"},
            {"no": "(5)", "expr": "1.6 = 16/10 = 8/__", "ans": "분모의 소인수:"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-2.png",
        "prompt": "다음은 기약분수의 분모를 소인수분해 한 것이다. 다음 분수를 유한소수로 나타낼 수 있으면 '유', 순환소수로 나타낼 수 있으면 '순'이라고 쓰시오.",
        "layout": "grid4",
        "items": [
            {"no": "(1)", "expr": "7/(2^2×3×5)", "ans": "(          )"},
            {"no": "(2)", "expr": "2/(3^2×5)", "ans": "(          )"},
            {"no": "(3)", "expr": "1/13", "ans": "(          )"},
            {"no": "(4)", "expr": "1/(2×5)", "ans": "(          )"},
        ],
    },
    {
        "kind": "problem",
        "header": "header-concept-practice-2.png",
        "prompt": "다음은 기약분수의 분모를 소인수분해 한 것이다. 다음 분수를 유한소수로 나타낼 수 있으면 '유', 순환소수로 나타낼 수 있으면 '순'이라고 쓰시오.",
        "layout": "grid4",
        "items": [
            {"no": "(5)", "expr": "11/(2×5)", "ans": "(          )"},
            {"no": "(6)", "expr": "5^2/(2×7)", "ans": "(          )"},
            {"no": "(7)", "expr": "7/(2^3×5^3)", "ans": "(          )"},
            {"no": "(8)", "expr": "2^5/(5^2×13)", "ans": "(          )"},
        ],
    },
    {"kind": "title", "title": "순환소수를 분수로 나타내기 (1)", "number": "03", "image_x": 11.343},
    {
        "kind": "problem",
        "header": "header-concept-practice-1.png",
        "prompt": "주어진 순환소수에서 처음 등장하는 순환마디에 ○표 하고, 그 순환마디의 앞과 뒤에 소수점이 놓이도록 화살표를 그리시오. (소수점이 이미 순환마디 앞에 있는 경우는 화살표를 하나만 그리기)",
        "layout": "page19",
        "items": [
            {"no": "(1)", "expr": "42.36784784...", "ans": ""},
            {"no": "(2)", "expr": "0.3555...", "ans": ""},
            {"no": "(3)", "expr": "0.666...", "ans": ""},
            {"no": "(4)", "expr": "1.252525...", "ans": ""},
        ],
    },
]


def qn(prefix: str, tag: str) -> str:
    return f"{{{NS[prefix]}}}{tag}"


def emu(value_in: float) -> str:
    return str(round(value_in * EMU))


def xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def available_font_names() -> set[str]:
    names: set[str] = set()
    if platform.system().lower() == "windows":
        font_dir = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        if font_dir.exists():
            for path in font_dir.iterdir():
                stem = path.stem.lower()
                if "nanum" in stem or "나눔" in stem:
                    names.add("나눔스퀘어라운드 ExtraBold")
                if "bt" in stem or "bt수식" in stem:
                    names.add("BT수식M")
    return names


def check_fonts(allow_missing: bool) -> dict:
    found = available_font_names()
    missing = [font for font in REQUIRED_FONTS if font not in found]
    if missing and not allow_missing:
        raise SystemExit(
            "Missing required fonts for deterministic rendering: "
            + ", ".join(missing)
            + ". Install the fonts or rerun with --allow-missing-fonts for validation-only generation."
        )
    return {"required": list(REQUIRED_FONTS), "detected": sorted(found), "missing": missing, "strict": not allow_missing}


def validate_pdf(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Input PDF not found: {path}")
    size = path.stat().st_size
    digest = sha256_file(path)
    if size != EXPECTED_PDF_SIZE or digest != EXPECTED_PDF_SHA256:
        raise SystemExit(
            "Unsupported PDF for deterministic unit1 10-19 generation. "
            f"Expected size={EXPECTED_PDF_SIZE}, sha256={EXPECTED_PDF_SHA256}; "
            f"got size={size}, sha256={digest}."
        )
    return {"path": str(path), "size": size, "sha256": digest}


def asset_manifest() -> dict:
    path = ASSET_DIR / "assets-manifest.json"
    if not path.exists():
        raise SystemExit(f"Missing unit1 assets manifest: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["assets"]:
        asset = ASSET_DIR / item["file"]
        if not asset.exists():
            raise SystemExit(f"Missing unit1 asset: {asset}")
        digest = sha256_file(asset)
        if digest != item["sha256"]:
            raise SystemExit(f"Asset hash mismatch for {asset}: {digest} != {item['sha256']}")
    return data


def style_parts_manifest() -> dict:
    path = STYLE_PARTS_DIR / "style-parts-manifest.json"
    if not path.exists():
        raise SystemExit(f"Missing unit1 OOXML style-parts manifest: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["parts"]:
        part = STYLE_PARTS_DIR / item["part"]
        if not part.exists():
            raise SystemExit(f"Missing unit1 OOXML style part: {part}")
        digest = sha256_file(part)
        if digest != item["sha256"]:
            raise SystemExit(f"Style part hash mismatch for {part}: {digest} != {item['sha256']}")
    return data


def presentation_metadata() -> dict:
    if not PRESENTATION_METADATA.exists():
        raise SystemExit(f"Missing unit1 presentation metadata: {PRESENTATION_METADATA}")
    digest = sha256_file(PRESENTATION_METADATA)
    if digest != PRESENTATION_METADATA_SHA256:
        raise SystemExit(
            f"Presentation metadata hash mismatch for {PRESENTATION_METADATA}: "
            f"{digest} != {PRESENTATION_METADATA_SHA256}"
        )
    return {"file": PRESENTATION_METADATA.name, "size_bytes": PRESENTATION_METADATA.stat().st_size, "sha256": digest}


def set_font(r_pr: etree._Element, font: str, color: str) -> None:
    solid = etree.SubElement(r_pr, qn("a", "solidFill"))
    etree.SubElement(solid, qn("a", "srgbClr"), val=color)
    etree.SubElement(r_pr, qn("a", "latin"), typeface=font)
    etree.SubElement(r_pr, qn("a", "ea"), typeface=font)
    etree.SubElement(r_pr, qn("a", "cs"), typeface="+mn-cs")


def font_size_attr(size: float) -> str:
    return str(round(size * 100))


def add_textbox(
    parent: etree._Element,
    ids,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    size: int = 24,
    font: str = "나눔스퀘어라운드 ExtraBold",
    color: str = "000000",
    bold: bool = False,
    name: str = "TextBox",
    align: str = "l",
    wrap: str = "square",
) -> etree._Element:
    sp = etree.SubElement(parent, qn("p", "sp"))
    nv = etree.SubElement(sp, qn("p", "nvSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=ids.next(), name=name)
    etree.SubElement(nv, qn("p", "cNvSpPr"), txBox="1")
    etree.SubElement(nv, qn("p", "nvPr"))
    sp_pr = etree.SubElement(sp, qn("p", "spPr"))
    xfrm = etree.SubElement(sp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(sp_pr, qn("a", "prstGeom"), prst="rect").append(etree.Element(qn("a", "avLst")))
    etree.SubElement(sp_pr, qn("a", "noFill"))
    tx = etree.SubElement(sp, qn("p", "txBody"))
    etree.SubElement(tx, qn("a", "bodyPr"), wrap=wrap, rtlCol="0")
    etree.SubElement(tx, qn("a", "lstStyle"))
    for line in text.split("\n"):
        p = etree.SubElement(tx, qn("a", "p"))
        etree.SubElement(p, qn("a", "pPr"), algn=align)
        r = etree.SubElement(p, qn("a", "r"))
        attrs = {"lang": "ko-KR", "sz": font_size_attr(size)}
        if bold:
            attrs["b"] = "1"
        r_pr = etree.SubElement(r, qn("a", "rPr"), **attrs)
        set_font(r_pr, font, color)
        etree.SubElement(r, qn("a", "t")).text = line
    return sp


def add_text_run(
    paragraph: etree._Element,
    text: str,
    *,
    size: int,
    font: str,
    color: str = "000000",
    bold: bool = False,
    baseline: int | None = None,
) -> None:
    if text == "":
        return
    r = etree.SubElement(paragraph, qn("a", "r"))
    attrs = {"lang": "ko-KR", "sz": font_size_attr(size)}
    if bold:
        attrs["b"] = "1"
    if baseline is not None:
        attrs["baseline"] = str(baseline)
    r_pr = etree.SubElement(r, qn("a", "rPr"), **attrs)
    set_font(r_pr, font, color)
    etree.SubElement(r, qn("a", "t")).text = text


def math_segments(text: str) -> list[tuple[str, bool]]:
    segments: list[tuple[str, bool]] = []
    i = 0
    normal: list[str] = []
    while i < len(text):
        if text[i] == "^" and i + 1 < len(text):
            if normal:
                segments.append(("".join(normal), False))
                normal = []
            i += 1
            sup: list[str] = []
            if text[i] == "{" and "}" in text[i + 1 :]:
                i += 1
                while i < len(text) and text[i] != "}":
                    sup.append(text[i])
                    i += 1
                i += 1
            else:
                while i < len(text) and re.match(r"[0-9A-Za-z가-힣+-]", text[i]):
                    sup.append(text[i])
                    i += 1
            segments.append(("".join(sup), True))
            continue
        normal.append(text[i])
        i += 1
    if normal:
        segments.append(("".join(normal), False))
    return segments


def add_math_textbox(
    parent: etree._Element,
    ids,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    size: int = 24,
    font: str = "BT수식M",
    color: str = "000000",
    bold: bool = True,
    name: str = "MathTextBox",
    align: str = "l",
    wrap: str = "none",
) -> etree._Element:
    sp = etree.SubElement(parent, qn("p", "sp"))
    nv = etree.SubElement(sp, qn("p", "nvSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=ids.next(), name=name)
    etree.SubElement(nv, qn("p", "cNvSpPr"), txBox="1")
    etree.SubElement(nv, qn("p", "nvPr"))
    sp_pr = etree.SubElement(sp, qn("p", "spPr"))
    xfrm = etree.SubElement(sp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(sp_pr, qn("a", "prstGeom"), prst="rect").append(etree.Element(qn("a", "avLst")))
    etree.SubElement(sp_pr, qn("a", "noFill"))
    tx = etree.SubElement(sp, qn("p", "txBody"))
    etree.SubElement(tx, qn("a", "bodyPr"), wrap=wrap, rtlCol="0")
    etree.SubElement(tx, qn("a", "lstStyle"))
    for line in text.split("\n"):
        p = etree.SubElement(tx, qn("a", "p"))
        etree.SubElement(p, qn("a", "pPr"), algn=align)
        for chunk, is_sup in math_segments(line):
            add_text_run(
                p,
                chunk,
                size=max(10, round(size * REFERENCE_SUPERSCRIPT_SIZE_RATIO)) if is_sup else size,
                font=font,
                color=color,
                bold=bold,
                baseline=REFERENCE_SUPERSCRIPT_BASELINE if is_sup else None,
            )
    return sp


def add_reference_title_number(
    parent: etree._Element,
    ids,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    fill: str | None = None,
    scheme_fill: str | None = None,
    outline: str | None = None,
    outline_width: str = "152400",
) -> etree._Element:
    sp = etree.SubElement(parent, qn("p", "sp"))
    nv = etree.SubElement(sp, qn("p", "nvSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=ids.next(), name="TextBox")
    etree.SubElement(nv, qn("p", "cNvSpPr"), txBox="1")
    etree.SubElement(nv, qn("p", "nvPr"))
    sp_pr = etree.SubElement(sp, qn("p", "spPr"))
    xfrm = etree.SubElement(sp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(sp_pr, qn("a", "prstGeom"), prst="rect").append(etree.Element(qn("a", "avLst")))
    etree.SubElement(sp_pr, qn("a", "noFill"))
    tx = etree.SubElement(sp, qn("p", "txBody"))
    body_pr = etree.SubElement(tx, qn("a", "bodyPr"), wrap="none", rtlCol="0")
    etree.SubElement(body_pr, qn("a", "spAutoFit"))
    etree.SubElement(tx, qn("a", "lstStyle"))
    p = etree.SubElement(tx, qn("a", "p"))
    r = etree.SubElement(p, qn("a", "r"))
    r_pr = etree.SubElement(r, qn("a", "rPr"), lang="en-US", altLang="ko-KR", sz=font_size_attr(70))
    if outline:
        ln = etree.SubElement(r_pr, qn("a", "ln"), w=outline_width)
        ln_solid = etree.SubElement(ln, qn("a", "solidFill"))
        etree.SubElement(ln_solid, qn("a", "srgbClr"), val=outline)
    solid = etree.SubElement(r_pr, qn("a", "solidFill"))
    if scheme_fill:
        etree.SubElement(solid, qn("a", "schemeClr"), val=scheme_fill)
    else:
        etree.SubElement(solid, qn("a", "srgbClr"), val=fill or "275184")
    for tag in ("latin", "ea"):
        etree.SubElement(r_pr, qn("a", tag), typeface="나눔스퀘어 ExtraBold")
    etree.SubElement(r, qn("a", "t")).text = text
    end_pr = etree.SubElement(p, qn("a", "endParaRPr"), lang="ko-KR", altLang="en-US", sz=font_size_attr(70))
    if outline:
        ln = etree.SubElement(end_pr, qn("a", "ln"), w=outline_width)
        ln_solid = etree.SubElement(ln, qn("a", "solidFill"))
        etree.SubElement(ln_solid, qn("a", "srgbClr"), val=outline)
    solid = etree.SubElement(end_pr, qn("a", "solidFill"))
    if scheme_fill:
        etree.SubElement(solid, qn("a", "schemeClr"), val=scheme_fill)
    else:
        etree.SubElement(solid, qn("a", "srgbClr"), val=fill or "275184")
    for tag in ("latin", "ea"):
        etree.SubElement(end_pr, qn("a", tag), typeface="나눔스퀘어 ExtraBold")
    return sp


def add_rect(
    parent: etree._Element,
    ids,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = "000000",
    line: str | None = None,
    line_width: str = "12700",
    radius: bool = False,
    name: str = "Rectangle",
) -> etree._Element:
    sp = etree.SubElement(parent, qn("p", "sp"))
    nv = etree.SubElement(sp, qn("p", "nvSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=ids.next(), name=name)
    etree.SubElement(nv, qn("p", "cNvSpPr"))
    etree.SubElement(nv, qn("p", "nvPr"))
    sp_pr = etree.SubElement(sp, qn("p", "spPr"))
    xfrm = etree.SubElement(sp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(sp_pr, qn("a", "prstGeom"), prst="roundRect" if radius else "rect").append(etree.Element(qn("a", "avLst")))
    solid = etree.SubElement(sp_pr, qn("a", "solidFill"))
    etree.SubElement(solid, qn("a", "srgbClr"), val=fill)
    ln = etree.SubElement(sp_pr, qn("a", "ln"), w=line_width)
    if line:
        ln_solid = etree.SubElement(ln, qn("a", "solidFill"))
        etree.SubElement(ln_solid, qn("a", "srgbClr"), val=line)
    else:
        etree.SubElement(ln, qn("a", "noFill"))
    return sp


def add_blank_box(parent: etree._Element, ids, x: float, y: float, w: float = REFERENCE_BLANK_BOX_SIZE, h: float = REFERENCE_BLANK_BOX_SIZE) -> None:
    add_rect(
        parent,
        ids,
        x,
        y,
        w,
        h,
        fill="FFFFFF",
        line="A6A6A6",
        line_width=REFERENCE_BLANK_LINE_WIDTH,
        radius=True,
        name="사각형: 둥근 모서리",
    )


def add_picture(parent: etree._Element, ids, rel_id: str, x: float, y: float, w: float, h: float, name: str) -> None:
    pic = etree.SubElement(parent, qn("p", "pic"))
    nv = etree.SubElement(pic, qn("p", "nvPicPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=ids.next(), name=name)
    c_pic = etree.SubElement(nv, qn("p", "cNvPicPr"))
    etree.SubElement(c_pic, qn("a", "picLocks"), noChangeAspect="1")
    etree.SubElement(nv, qn("p", "nvPr"))
    blip_fill = etree.SubElement(pic, qn("p", "blipFill"))
    etree.SubElement(blip_fill, qn("a", "blip"), **{qn("r", "embed"): rel_id})
    stretch = etree.SubElement(blip_fill, qn("a", "stretch"))
    etree.SubElement(stretch, qn("a", "fillRect"))
    sp_pr = etree.SubElement(pic, qn("p", "spPr"))
    xfrm = etree.SubElement(sp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(sp_pr, qn("a", "prstGeom"), prst="rect").append(etree.Element(qn("a", "avLst")))


class Ids:
    def __init__(self) -> None:
        self.value = 1

    def next(self) -> str:
        self.value += 1
        return str(self.value)


def split_fraction_token(token: str) -> tuple[str, str] | None:
    if token.count("/") != 1:
        return None
    numerator, denominator = token.split("/", 1)
    if not numerator or not denominator:
        return None
    if numerator.startswith("(") or numerator.endswith(")"):
        return None
    if denominator.startswith("(") and denominator.endswith(")"):
        denominator = denominator[1:-1]
    return numerator, denominator


def estimated_math_width(text: str, size: int = 24) -> float:
    return max(0.16, len(text) * 0.105 * (size / 24))


def estimated_exponent_expression_width(text: str, size: int = 24) -> float:
    scale = size / 24
    width = 0.0
    i = 0
    while i < len(text):
        if text[i] == "^" and i + 1 < len(text):
            i += 1
            if text[i] == "{" and "}" in text[i + 1 :]:
                i += 1
                sup = []
                while i < len(text) and text[i] != "}":
                    sup.append(text[i])
                    i += 1
                i += 1
            else:
                sup = []
                while i < len(text) and re.match(r"[0-9A-Za-z가-힣+-]", text[i]):
                    sup.append(text[i])
                    i += 1
            width += max(0.10, len(sup) * 0.10) * scale
            continue
        width += (0.23 if text[i] == "×" else 0.17) * scale
        i += 1
    return max(0.55, width + 0.28 * scale)


def blank_box_size(size: int) -> tuple[float, float]:
    scale = size / 16
    return max(0.39, 0.39 * scale), max(0.33, 0.39 * scale)


def denominator_pattern_width(pattern: str, size: int = 16) -> float:
    if "__" not in pattern:
        if "^" in pattern:
            return estimated_exponent_expression_width(pattern, size)
        return estimated_math_width(pattern, size)
    blank_w, _ = blank_box_size(size)
    scale = size / 16
    width = 0.0
    i = 0
    while i < len(pattern):
        if pattern.startswith("__", i):
            width += blank_w
            i += 2
            if i < len(pattern) and pattern[i] == "^":
                i += 1
                sup = []
                while i < len(pattern) and re.match(r"[0-9A-Za-z가-힣+-]", pattern[i]):
                    sup.append(pattern[i])
                    i += 1
                width += max(0.12, len(sup) * 0.10 * scale)
                width += 0.07 * scale
            continue
        if pattern[i] == "×":
            width += 0.34 * scale
            i += 1
            continue
        run = []
        while i < len(pattern) and not pattern.startswith("__", i) and pattern[i] not in {"×", "^"}:
            run.append(pattern[i])
            i += 1
        if run:
            width += estimated_math_width("".join(run), size)
            continue
        i += 1
    return max(0.55, width)


def stacked_fraction_width(numerator: str, denominator: str, size: int = 16, min_width: float = 0.55) -> float:
    numerator_w = estimated_math_width(numerator, size)
    denominator_w = denominator_pattern_width(denominator, size)
    return max(min_width, numerator_w + 0.18, denominator_w + 0.14)


def add_denominator_pattern(parent: etree._Element, ids, x: float, y: float, pattern: str, *, size: int = 16) -> float:
    blank_w, blank_h = blank_box_size(size)
    scale = size / 16
    cursor = x
    i = 0
    while i < len(pattern):
        if pattern.startswith("__", i):
            add_blank_box(parent, ids, cursor, y + 0.03, blank_w, blank_h)
            cursor += blank_w
            i += 2
            if i < len(pattern) and pattern[i] == "^":
                i += 1
                sup = []
                while i < len(pattern) and re.match(r"[0-9A-Za-z가-힣+-]", pattern[i]):
                    sup.append(pattern[i])
                    i += 1
                sup_text = "".join(sup)
                sup_w = max(0.14, len(sup_text) * 0.10 * scale)
                add_math_textbox(
                    parent,
                    ids,
                    cursor - 0.01,
                    y - 0.06,
                    sup_w,
                    0.22,
                    sup_text,
                    size=max(9, round(size * 0.68)),
                    font="BT수식M",
                    bold=True,
                    wrap="none",
                )
                cursor += sup_w + 0.07 * scale
            continue
        if pattern[i] == "×":
            mult_w = 0.34 * scale
            add_math_textbox(parent, ids, cursor + 0.05 * scale, y + 0.03, mult_w, 0.32, "×", size=size, font="BT수식M", bold=True, wrap="none")
            cursor += mult_w
            i += 1
            continue
        run = []
        while i < len(pattern) and not pattern.startswith("__", i) and pattern[i] not in {"×", "^"}:
            run.append(pattern[i])
            i += 1
        if run:
            run_text = "".join(run)
            run_w = estimated_math_width(run_text, size)
            add_math_textbox(parent, ids, cursor, y + 0.02, run_w, 0.34, run_text, size=size, font="BT수식M", bold=True, wrap="none")
            cursor += run_w
            continue
        i += 1
    return cursor - x


def fraction_layout(style: str) -> dict[str, float]:
    if style == "page10":
        return {
            "x_offset": PAGE10_FRACTION_X_OFFSET,
            "num_y": PAGE10_FRACTION_NUMERATOR_Y_OFFSET,
            "bar_y": PAGE10_FRACTION_BAR_Y_OFFSET,
            "den_y": PAGE10_FRACTION_DENOMINATOR_Y_OFFSET,
            "pattern_y": PAGE10_FRACTION_DENOMINATOR_Y_OFFSET,
            "min_width": PAGE10_FRACTION_MIN_WIDTH,
        }
    if style == "page14":
        return {
            "x_offset": 0.0,
            "num_y": PAGE14_FRACTION_NUMERATOR_Y_OFFSET,
            "bar_y": PAGE14_FRACTION_BAR_Y_OFFSET,
            "den_y": PAGE14_FRACTION_DENOMINATOR_Y_OFFSET,
            "pattern_y": PAGE14_FRACTION_PATTERN_Y_OFFSET,
            "min_width": PAGE14_FRACTION_MIN_WIDTH,
        }
    return {
        "x_offset": 0.0,
        "num_y": INLINE_FRACTION_NUMERATOR_Y_OFFSET,
        "bar_y": INLINE_FRACTION_BAR_Y_OFFSET,
        "den_y": INLINE_FRACTION_DENOMINATOR_Y_OFFSET,
        "pattern_y": INLINE_FRACTION_DENOMINATOR_Y_OFFSET,
        "min_width": 0.55,
    }


def reference_decimal_ellipsis(text: str) -> str:
    return text.replace("...", REFERENCE_DECIMAL_ELLIPSIS)


def add_fraction_at(parent: etree._Element, ids, x: float, y: float, numerator: str, denominator: str, *, size: int = 22, style: str = "default") -> float:
    layout = fraction_layout(style)
    x = x + layout["x_offset"]
    frac_size = max(16, round(size * 24 / 22))
    frac_w = stacked_fraction_width(numerator, denominator, frac_size, min_width=layout["min_width"])
    add_math_textbox(parent, ids, x, y + layout["num_y"], frac_w, 0.42, numerator, size=frac_size, font="BT수식M", bold=True, align="ctr", wrap="none")
    add_rect(parent, ids, x, y + layout["bar_y"], frac_w, 0.018, fill="000000", name="Fraction bar")
    if "__" in denominator:
        pattern_w = denominator_pattern_width(denominator, frac_size)
        add_denominator_pattern(parent, ids, x + (frac_w - pattern_w) / 2, y + layout["pattern_y"] + 0.03, denominator, size=frac_size)
    else:
        add_math_textbox(parent, ids, x, y + layout["den_y"], frac_w, 0.42, denominator, size=frac_size, font="BT수식M", bold=True, align="ctr", wrap="none")
    return layout["x_offset"] + frac_w


def add_inline_formula(parent: etree._Element, ids, x: float, y: float, w: float, text: str, *, size: int = 24, fraction_style: str = "default") -> None:
    cursor = x
    max_x = x + w
    layout = fraction_layout(fraction_style)
    for part in re.findall(r"\s+|\S+", text):
        if cursor >= max_x:
            break
        if part.isspace():
            cursor += min(0.18, 0.07 * len(part))
            continue
        fraction = split_fraction_token(part)
        if fraction is None:
            part_w = min(estimated_math_width(part, size), max_x - cursor)
            add_math_textbox(parent, ids, cursor, y, part_w, 0.56, part, size=size, font="BT수식M", bold=True, wrap="none")
            cursor += part_w + 0.07
            continue
        numerator, denominator = fraction
        frac_size = max(16, round(size * 24 / 23))
        frac_w = min(stacked_fraction_width(numerator, denominator, frac_size, min_width=layout["min_width"]), max_x - cursor)
        add_math_textbox(parent, ids, cursor, y + layout["num_y"], frac_w, 0.42, numerator, size=frac_size, font="BT수식M", bold=True, align="ctr", wrap="none")
        add_rect(parent, ids, cursor, y + layout["bar_y"], frac_w, 0.018, fill="000000", name="Fraction bar")
        if "__" in denominator:
            pattern_w = denominator_pattern_width(denominator, frac_size)
            add_denominator_pattern(parent, ids, cursor + (frac_w - pattern_w) / 2, y + layout["pattern_y"] + 0.03, denominator, size=frac_size)
        else:
            add_math_textbox(parent, ids, cursor, y + layout["den_y"], frac_w, 0.42, denominator, size=frac_size, font="BT수식M", bold=True, align="ctr", wrap="none")
        cursor += frac_w + 0.10


def add_conversion_formula(parent: etree._Element, ids, x: float, y: float, text: str) -> None:
    numerator, denominator = re.match(r"([^/\s]+)/([^=\s]+)", text).groups()
    add_fraction_at(parent, ids, x, y, numerator, denominator, size=22, style="page10")
    eq_x = x + 0.36
    b1_x = x + 0.85
    div_x = x + 1.47
    b2_x = x + 1.80
    eq2_x = x + 2.43
    add_textbox(parent, ids, eq_x, y, 0.22, 0.52, "=", size=24, font="BT수식M", bold=True, wrap="none")
    add_blank_box(parent, ids, b1_x, y - 0.01)
    add_textbox(parent, ids, div_x, y, 0.22, 0.52, "÷", size=24, font="BT수식M", bold=True, wrap="none")
    add_blank_box(parent, ids, b2_x, y - 0.01)
    add_textbox(parent, ids, eq2_x, y, 0.22, 0.52, "=", size=24, font="BT수식M", bold=True, wrap="none")


def add_group(parent: etree._Element, ids, x: float, y: float, w: float, h: float) -> tuple[etree._Element, str]:
    group_id = ids.next()
    group = etree.SubElement(parent, qn("p", "grpSp"))
    nv = etree.SubElement(group, qn("p", "nvGrpSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id=group_id, name=f"그룹 {group_id}")
    etree.SubElement(nv, qn("p", "cNvGrpSpPr"))
    etree.SubElement(nv, qn("p", "nvPr"))
    grp_pr = etree.SubElement(group, qn("p", "grpSpPr"))
    xfrm = etree.SubElement(grp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "ext"), cx=emu(w), cy=emu(h))
    etree.SubElement(xfrm, qn("a", "chOff"), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn("a", "chExt"), cx=emu(w), cy=emu(h))
    return group, group_id


def layout_positions(layout: str, count: int) -> list[dict[str, float]]:
    if layout in {"page10_a", "page10_b"}:
        return [
            {"no_x": 0.28, "expr_x": 0.96, "ans_x": 6.23, "y": 2.22 + i * 1.42, "expr_w": 4.85, "ans_w": 2.76}
            for i in range(count)
        ]
    if layout == "tworow":
        return [
            {"no_x": 0.28, "expr_x": 0.96, "ans_x": 3.25, "y": 2.42, "expr_w": 2.05, "ans_w": 3.40},
            {"no_x": 5.15, "expr_x": 5.86, "ans_x": 8.15, "y": 2.42, "expr_w": 2.05, "ans_w": 3.40},
        ][:count]
    if layout == "grid4":
        return [
            {"no_x": 0.246, "expr_x": 1.076, "ans_x": 3.061, "y": 3.371, "ans_y": 3.246, "expr_w": 2.05, "ans_w": 1.285},
            {"no_x": 5.423, "expr_x": 6.285, "ans_x": 8.238, "y": 3.371, "ans_y": 3.246, "expr_w": 1.75, "ans_w": 1.285},
            {"no_x": 0.246, "expr_x": 1.357, "ans_x": 3.061, "y": 5.246, "ans_y": 5.120, "expr_w": 1.45, "ans_w": 1.285},
            {"no_x": 5.423, "expr_x": 6.285, "ans_x": 8.238, "y": 5.246, "ans_y": 5.120, "expr_w": 1.75, "ans_w": 1.285},
        ][:count]
    if layout == "page19":
        return [
            {"no_x": 0.28, "expr_x": 0.96, "ans_x": 0.0, "y": 2.65, "expr_w": 3.40, "ans_w": 0.1},
            {"no_x": 5.20, "expr_x": 5.90, "ans_x": 0.0, "y": 2.65, "expr_w": 2.40, "ans_w": 0.1},
            {"no_x": 0.28, "expr_x": 0.96, "ans_x": 0.0, "y": 4.45, "expr_w": 2.40, "ans_w": 0.1},
            {"no_x": 5.20, "expr_x": 5.90, "ans_x": 0.0, "y": 4.45, "expr_w": 2.60, "ans_w": 0.1},
        ][:count]
    return [
        {"no_x": 0.28, "expr_x": 0.96, "ans_x": 7.15, "y": 2.35 + i * 1.28, "expr_w": 5.90, "ans_w": 3.40}
        for i in range(count)
    ]


def add_item(parent: etree._Element, ids, item: dict, pos: dict[str, float], *, layout: str = "") -> None:
    y = pos["y"]
    ans_y = pos.get("ans_y", y)
    add_textbox(parent, ids, pos["no_x"], y, 0.65, 0.50, item["no"], size=23, wrap="none")
    expr = reference_decimal_ellipsis(item["expr"])
    if item.get("blank_formula"):
        add_conversion_formula(parent, ids, pos["expr_x"], y, expr)
    elif "/" in expr:
        if layout in {"page10_a", "page10_b"}:
            fraction_style = "page10"
        elif layout in {"page14_a", "page14_b"}:
            fraction_style = "page14"
        else:
            fraction_style = "default"
        add_inline_formula(parent, ids, pos["expr_x"], y, pos["expr_w"], expr, size=23, fraction_style=fraction_style)
    else:
        add_math_textbox(parent, ids, pos["expr_x"], y, pos["expr_w"], 0.58, expr, size=23, font="BT수식M", bold=True, wrap="none")
    if item.get("ans"):
        if re.fullmatch(r"\(\s*\)", item["ans"]):
            add_textbox(parent, ids, pos["ans_x"], ans_y, pos["ans_w"], 0.505, item["ans"], size=24, font="BT수식M", bold=True, wrap="none")
        else:
            font = "나눔스퀘어라운드 ExtraBold" if re.search(r"[가-힣]", item["ans"]) else "BT수식M"
            add_textbox(parent, ids, pos["ans_x"], ans_y, pos["ans_w"], 0.78, item["ans"], size=21, font=font, wrap="square")


def add_problem_items(parent: etree._Element, ids, spec: dict) -> list[str]:
    targets: list[str] = []
    positions = layout_positions(spec["layout"], len(spec["items"]))
    for idx, (item, pos) in enumerate(zip(spec["items"], positions)):
        if idx == 0:
            add_item(parent, ids, item, pos, layout=spec["layout"])
            continue
        x = min(pos["no_x"], pos["expr_x"], pos["ans_x"] if pos["ans_x"] else pos["expr_x"])
        group_has_fraction = "/" in item["expr"]
        y = pos["y"] - (0.52 if group_has_fraction else 0.04)
        h = 1.22 if group_has_fraction else 0.90
        w = max(pos["expr_x"] + pos["expr_w"], pos["ans_x"] + pos["ans_w"] if pos["ans_x"] else pos["expr_x"] + pos["expr_w"]) - x
        group, group_id = add_group(parent, ids, x, y, w, h)
        add_item(group, ids, item, pos, layout=spec["layout"])
        targets.append(group_id)
    return targets


def timing_branch(target_id: str, ids: tuple[int, int, int, int]) -> etree._Element:
    outer_id, inner_id, effect_id, set_id = ids
    par1 = etree.Element(qn("p", "par"))
    ctn1 = etree.SubElement(par1, qn("p", "cTn"), id=str(outer_id), fill="hold")
    st1 = etree.SubElement(ctn1, qn("p", "stCondLst"))
    etree.SubElement(st1, qn("p", "cond"), delay="indefinite")
    child1 = etree.SubElement(ctn1, qn("p", "childTnLst"))
    par2 = etree.SubElement(child1, qn("p", "par"))
    ctn2 = etree.SubElement(par2, qn("p", "cTn"), id=str(inner_id), fill="hold")
    st2 = etree.SubElement(ctn2, qn("p", "stCondLst"))
    etree.SubElement(st2, qn("p", "cond"), delay="0")
    child2 = etree.SubElement(ctn2, qn("p", "childTnLst"))
    par3 = etree.SubElement(child2, qn("p", "par"))
    ctn3 = etree.SubElement(par3, qn("p", "cTn"), id=str(effect_id), presetID="1", presetClass="entr", presetSubtype="0", fill="hold", nodeType="clickEffect")
    st3 = etree.SubElement(ctn3, qn("p", "stCondLst"))
    etree.SubElement(st3, qn("p", "cond"), delay="0")
    child3 = etree.SubElement(ctn3, qn("p", "childTnLst"))
    set_node = etree.SubElement(child3, qn("p", "set"))
    c_bhvr = etree.SubElement(set_node, qn("p", "cBhvr"))
    ctn4 = etree.SubElement(c_bhvr, qn("p", "cTn"), id=str(set_id), dur="1", fill="hold")
    st4 = etree.SubElement(ctn4, qn("p", "stCondLst"))
    etree.SubElement(st4, qn("p", "cond"), delay="0")
    tgt_el = etree.SubElement(c_bhvr, qn("p", "tgtEl"))
    etree.SubElement(tgt_el, qn("p", "spTgt"), spid=target_id)
    attrs = etree.SubElement(c_bhvr, qn("p", "attrNameLst"))
    etree.SubElement(attrs, qn("p", "attrName")).text = "style.visibility"
    to = etree.SubElement(set_node, qn("p", "to"))
    etree.SubElement(to, qn("p", "strVal"), val="visible")
    return par1


def build_timing(target_ids: list[str]) -> etree._Element:
    timing = etree.Element(qn("p", "timing"))
    tn_lst = etree.SubElement(timing, qn("p", "tnLst"))
    root_par = etree.SubElement(tn_lst, qn("p", "par"))
    root_ctn = etree.SubElement(root_par, qn("p", "cTn"), id="1", dur="indefinite", restart="never", nodeType="tmRoot")
    root_child = etree.SubElement(root_ctn, qn("p", "childTnLst"))
    seq = etree.SubElement(root_child, qn("p", "seq"), concurrent="1", nextAc="seek")
    seq_ctn = etree.SubElement(seq, qn("p", "cTn"), id="2", dur="indefinite", nodeType="mainSeq")
    child = etree.SubElement(seq_ctn, qn("p", "childTnLst"))
    next_id = 3
    for target in target_ids:
        child.append(timing_branch(target, (next_id, next_id + 1, next_id + 2, next_id + 3)))
        next_id += 4
    for tag, evt in (("prevCondLst", "onPrev"), ("nextCondLst", "onNext")):
        cond_lst = etree.SubElement(seq, qn("p", tag))
        cond = etree.SubElement(cond_lst, qn("p", "cond"), evt=evt, delay="0")
        tgt = etree.SubElement(cond, qn("p", "tgtEl"))
        etree.SubElement(tgt, qn("p", "sldTgt"))
    return timing


def base_slide() -> tuple[etree._Element, etree._Element, Ids]:
    slide = etree.Element(qn("p", "sld"), nsmap={"a": NS["a"], "r": NS["r"], "p": NS["p"]})
    c_sld = etree.SubElement(slide, qn("p", "cSld"))
    sp_tree = etree.SubElement(c_sld, qn("p", "spTree"))
    nv = etree.SubElement(sp_tree, qn("p", "nvGrpSpPr"))
    etree.SubElement(nv, qn("p", "cNvPr"), id="1", name="")
    etree.SubElement(nv, qn("p", "cNvGrpSpPr"))
    etree.SubElement(nv, qn("p", "nvPr"))
    grp_pr = etree.SubElement(sp_tree, qn("p", "grpSpPr"))
    xfrm = etree.SubElement(grp_pr, qn("a", "xfrm"))
    etree.SubElement(xfrm, qn("a", "off"), x="0", y="0")
    etree.SubElement(xfrm, qn("a", "ext"), cx="0", cy="0")
    etree.SubElement(xfrm, qn("a", "chOff"), x="0", y="0")
    etree.SubElement(xfrm, qn("a", "chExt"), cx="0", cy="0")
    clr_map_ovr = etree.SubElement(slide, qn("p", "clrMapOvr"))
    etree.SubElement(clr_map_ovr, qn("a", "masterClrMapping"))
    return slide, sp_tree, Ids()


def create_title_slide(spec: dict) -> tuple[bytes, bytes]:
    slide, sp_tree, ids = base_slide()
    if spec["number"] == "01":
        add_textbox(sp_tree, ids, 4.244, 2.788, 2.893, 0.774, spec["title"], size=40, bold=False, wrap="none")
        add_reference_title_number(sp_tree, ids, 2.794, 2.527, 1.419, 1.279, spec["number"], fill="275184", outline="275184")
        add_reference_title_number(sp_tree, ids, 2.794, 2.527, 1.419, 1.279, spec["number"], scheme_fill="bg1")
    elif spec["number"] == "02":
        add_textbox(sp_tree, ids, 2.477, 2.788, 8.380, 0.774, f"{spec['number']}. {spec['title']}", size=40, bold=False, wrap="none")
    else:
        add_textbox(sp_tree, ids, 2.871, 2.788, 8.343, 0.774, f"{spec['number']}.{spec['title']}", size=40, bold=False, wrap="none")
    add_rect(sp_tree, ids, 2.458, 2.333, 0.716, 0.293, fill="F9EA5B", radius=True, name="사각형: 둥근 모서리")
    add_textbox(sp_tree, ids, 2.449, 2.341, 0.735, 0.278, "개념핵심", size=10.5, color="275184", bold=False, wrap="none")
    add_picture(sp_tree, ids, "rId2", spec["image_x"], 2.36, 1.529, 1.578, "title-character.png")
    return xml_bytes(slide), slide_rels("slideLayout3.xml", {"rId2": "title-character.png"})


def create_problem_slide(spec: dict) -> tuple[bytes, bytes]:
    slide, sp_tree, ids = base_slide()
    add_picture(sp_tree, ids, "rId2", 0.283, 0.528, 1.937, 0.463, spec["header"])
    prompt_h = 0.68 if len(spec["prompt"]) < 70 else 1.18
    add_textbox(sp_tree, ids, 0.224, 0.993, 10.55, prompt_h, spec["prompt"], size=24, bold=True, wrap="square")
    targets = add_problem_items(sp_tree, ids, spec)
    if targets:
        slide.append(build_timing(targets))
    return xml_bytes(slide), slide_rels("slideLayout2.xml", {"rId2": spec["header"]})


def slide_rels(layout_file: str, images: dict[str, str]) -> bytes:
    root = etree.Element(qn("rel", "Relationships"), nsmap={None: NS["rel"]})
    etree.SubElement(
        root,
        qn("rel", "Relationship"),
        Id="rId1",
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
        Target=f"../slideLayouts/{layout_file}",
    )
    for rel_id, filename in images.items():
        etree.SubElement(
            root,
            qn("rel", "Relationship"),
            Id=rel_id,
            Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
            Target=f"../media/{filename}",
        )
    return xml_bytes(root)


def content_types() -> bytes:
    root = etree.Element(qn("ct", "Types"), nsmap={None: NS["ct"]})
    etree.SubElement(root, qn("ct", "Default"), Extension="rels", ContentType="application/vnd.openxmlformats-package.relationships+xml")
    etree.SubElement(root, qn("ct", "Default"), Extension="xml", ContentType="application/xml")
    etree.SubElement(root, qn("ct", "Default"), Extension="png", ContentType="image/png")
    overrides = {
        "/ppt/presentation.xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
        "/docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
        "/docProps/app.xml": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
    }
    for part, ctype in STYLE_PART_CONTENT_TYPES.items():
        overrides[f"/{part}"] = ctype
    for idx in range(1, len(SLIDE_PLAN) + 1):
        overrides[f"/ppt/slides/slide{idx}.xml"] = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
    for part, ctype in overrides.items():
        etree.SubElement(root, qn("ct", "Override"), PartName=part, ContentType=ctype)
    return xml_bytes(root)


def root_rels() -> bytes:
    root = etree.Element(qn("rel", "Relationships"), nsmap={None: NS["rel"]})
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId1", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", Target="ppt/presentation.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId2", Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", Target="docProps/core.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId3", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", Target="docProps/app.xml")
    return xml_bytes(root)


def presentation_xml() -> bytes:
    return PRESENTATION_METADATA.read_bytes()


def presentation_rels() -> bytes:
    root = etree.Element(qn("rel", "Relationships"), nsmap={None: NS["rel"]})
    etree.SubElement(
        root,
        qn("rel", "Relationship"),
        Id="rId1",
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster",
        Target="slideMasters/slideMaster1.xml",
    )
    etree.SubElement(
        root,
        qn("rel", "Relationship"),
        Id="rId2",
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster",
        Target="slideMasters/slideMaster2.xml",
    )
    for idx in range(1, len(SLIDE_PLAN) + 1):
        etree.SubElement(root, qn("rel", "Relationship"), Id=f"rId{idx + 2}", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", Target=f"slides/slide{idx}.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId15", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps", Target="presProps.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId16", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps", Target="viewProps.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId17", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles", Target="tableStyles.xml")
    etree.SubElement(root, qn("rel", "Relationship"), Id="rId18", Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", Target="theme/theme1.xml")
    return xml_bytes(root)


def core_xml() -> bytes:
    root = etree.Element(
        qn("cp", "coreProperties"),
        nsmap={"cp": NS["cp"], "dc": NS["dc"], "dcterms": NS["dcterms"], "xsi": NS["xsi"]},
    )
    etree.SubElement(root, qn("dc", "title")).text = "중등수학 2-1 10-19 개념익히기"
    etree.SubElement(root, qn("dc", "creator")).text = "pdf2concept-problem-pptx"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    etree.SubElement(root, qn("dcterms", "created"), {qn("xsi", "type"): "dcterms:W3CDTF"}).text = now
    return xml_bytes(root)


def app_xml() -> bytes:
    root = etree.Element("Properties", nsmap={None: "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties", "vt": NS["vt"]})
    etree.SubElement(root, "Application").text = "pdf2concept-problem-pptx"
    etree.SubElement(root, "Slides").text = str(len(SLIDE_PLAN))
    return xml_bytes(root)


def build_deck(output: Path, pdf_info: dict, font_info: dict, assets: dict, style_parts: dict, presentation_meta: dict) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    slides: dict[str, bytes] = {}
    rels: dict[str, bytes] = {}
    for idx, spec in enumerate(SLIDE_PLAN, start=1):
        if spec["kind"] == "title":
            slide, rel = create_title_slide(spec)
        else:
            slide, rel = create_problem_slide(spec)
        slides[f"ppt/slides/slide{idx}.xml"] = slide
        rels[f"ppt/slides/_rels/slide{idx}.xml.rels"] = rel

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as deck:
        deck.writestr("[Content_Types].xml", content_types())
        deck.writestr("_rels/.rels", root_rels())
        deck.writestr("docProps/core.xml", core_xml())
        deck.writestr("docProps/app.xml", app_xml())
        deck.writestr("ppt/presentation.xml", presentation_xml())
        deck.writestr("ppt/_rels/presentation.xml.rels", presentation_rels())
        for item in style_parts["parts"]:
            deck.write(STYLE_PARTS_DIR / item["part"], item["part"])
        for name, data in slides.items():
            deck.writestr(name, data)
        for name, data in rels.items():
            deck.writestr(name, data)
        for item in assets["assets"]:
            deck.write(ASSET_DIR / item["file"], f"ppt/media/{item['file']}")

    return {
        "output": str(output),
        "source_pdf": pdf_info,
        "requested_pdf_pages": "10-19",
        "included_concept_practice_pages": [10, 11, 14, 15, 19],
        "excluded_pages_in_requested_range": {
            "12": "개념 다지기",
            "13": "개념 마무리",
            "16": "개념 다지기",
            "17": "개념 마무리",
            "18": "개념핵심 설명 페이지이며 개념익히기 문제 없음",
        },
        "slide_count": len(SLIDE_PLAN),
        "runtime_reference_pptx_used": False,
        "editable_reconstruction": True,
        "image_problem_crops_used": False,
        "page14_denominator_blank_patterns": {
            "slide7_item1": "3/(__^2×__)",
            "slide7_item2": "11/(__^2×__^2)",
            "slide8_item3": "2/__",
            "slide8_item4": "1/(__^3)",
            "slide8_item5": "8/__",
        },
        "decimal_ellipsis_style": {
            "reference_character": REFERENCE_DECIMAL_ELLIPSIS,
            "unicode": "U+2026",
            "rule": "Use the reference horizontal ellipsis character for recurring-decimal shorthand; do not render decimal continuation as three baseline periods."
        },
        "cover_slide_style": {
            "slide1_number_structure": "Two overlaid 01 text boxes: blue fill with blue text outline width 152400 EMU, then bg1 fill on top.",
            "slide1_label": "Yellow rounded rectangle F9EA5B with blue 개념핵심 text.",
            "slide6_title": "Inline number title text: 02. 유한소수로 나타낼 수 있는 분수.",
            "slide11_title": "Inline number title text: 03.순환소수를 분수로 나타내기 (1)."
        },
        "page15_grid_layout": {
            "rule": "Use measured reference grid anchors for the two-column factorization slide; do not use the high fallback grid.",
            "top_left": {"no_x": 0.246, "expr_x": 1.076, "ans_x": 3.061, "y": 3.371, "ans_y": 3.246},
            "top_right": {"no_x": 5.423, "expr_x": 6.285, "ans_x": 8.238, "y": 3.371, "ans_y": 3.246},
            "bottom_left": {"no_x": 0.246, "expr_x": 1.357, "ans_x": 3.061, "y": 5.246, "ans_y": 5.120},
            "bottom_right": {"no_x": 5.423, "expr_x": 6.285, "ans_x": 8.238, "y": 5.246, "ans_y": 5.120}
        },
        "stacked_fraction_style": {
            "unit1_page10_problem_fraction_run_size": 24,
            "unit1_page10_consistency_rule": "Use the same numerator/denominator run size for one-digit and two-digit fractions such as 1/7, 19/10, and 1/5.",
            "unit1_page10_fraction_offsets_in": {
                "x": PAGE10_FRACTION_X_OFFSET,
                "numerator_y": PAGE10_FRACTION_NUMERATOR_Y_OFFSET,
                "fraction_bar_y": PAGE10_FRACTION_BAR_Y_OFFSET,
                "denominator_y": PAGE10_FRACTION_DENOMINATOR_Y_OFFSET
            },
            "unit1_page10_blank_box_size_in": REFERENCE_BLANK_BOX_SIZE,
            "unit1_page10_blank_line_width_emu": int(REFERENCE_BLANK_LINE_WIDTH),
            "unit1_page10_answer_parentheses_wrap": "none",
            "unit1_page14_fraction_offsets_in": {
                "numerator_y": PAGE14_FRACTION_NUMERATOR_Y_OFFSET,
                "fraction_bar_y": PAGE14_FRACTION_BAR_Y_OFFSET,
                "denominator_y": PAGE14_FRACTION_DENOMINATOR_Y_OFFSET,
                "blank_pattern_y": PAGE14_FRACTION_PATTERN_Y_OFFSET
            },
            "unit1_page14_rule": "Align fraction bars in chained equalities with the visual centerline of adjacent equals signs.",
            "unit1_page15_exponent_run_size": 20,
            "unit1_page15_exponent_baseline": REFERENCE_SUPERSCRIPT_BASELINE,
        },
        "font_preflight": font_info,
        "assets": assets,
        "presentation_metadata": presentation_meta,
        "ooxml_style_parts": style_parts,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate the deterministic unit 1 pages 10-19 concept-practice PPTX.")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-missing-fonts", action="store_true", help="Skip strict font failure; use only for validation on machines without the required fonts.")
    args = parser.parse_args(argv)

    pdf_info = validate_pdf(args.pdf)
    font_info = check_fonts(args.allow_missing_fonts)
    assets = asset_manifest()
    style_parts = style_parts_manifest()
    presentation_meta = presentation_metadata()
    report = build_deck(args.output, pdf_info, font_info, assets, style_parts, presentation_meta)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
