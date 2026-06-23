# pdf2concept-problem-pptx skill workspace

이 저장소는 PDF 원고의 `개념 익히기` 문제만 추출해 16:9 강의용 PPTX로 재구성하는 Codex 스킬을 담고 있습니다.

## 포함 범위

- 스킬 본체: `.codex/skills/pdf2concept-problem-pptx`
- 내부 디자인 계약: `.codex/skills/pdf2concept-problem-pptx/assets/design/style-map.json`
- 공용 스타일 자산: `.codex/skills/pdf2concept-problem-pptx/assets/concept-practice-style`
- 생성/검증 스크립트: `.codex/skills/pdf2concept-problem-pptx/scripts`

입력 PDF, 생성 PPTX, `.generated/`, `기대결과/`는 커밋 대상이 아닙니다.

## 설치

Python 3.10 이상을 사용합니다.

```powershell
python -m pip install -r requirements.txt
```

동일한 시각 결과를 위해 대상 PC에 다음 폰트가 설치되어 있어야 합니다.

- `나눔스퀘어라운드 ExtraBold`
- `나눔스퀘어 ExtraBold`
- `BT수식M`

## 스킬 자체 점검

공유 전 또는 스킬 변경 후 먼저 self-check를 실행합니다.

```powershell
python .codex\skills\pdf2concept-problem-pptx\scripts\self_check_skill.py `
  --report ".generated\self-check-report.json"
```

`passes: true`가 나와야 합니다.

## PPTX 생성

표준 진입점은 `build_concept_practice_deck.py`입니다. 이 스크립트는 PPTX 생성 후 generation report, editable deck, OOXML style, reference pattern 검증을 한 번에 실행합니다.

```powershell
python .codex\skills\pdf2concept-problem-pptx\scripts\build_concept_practice_deck.py `
  --pdf "중등수학 2-1본문학생용(001-188)_SPOT.pdf" `
  --pages 28-59 `
  --output ".generated\중등수학_2-1_28-59_개념익히기.pptx" `
  --report-dir ".generated\중등수학_2-1_28-59_reports"
```

성공 기준은 report 폴더의 `build-summary.json`에서 `passes: true`입니다.

## 산출 report

빌드 러너는 다음 파일을 생성합니다.

- `generation-report.json`: 추출된 페이지, 문항, 슬라이드 추적
- `generation-report-validation.json`: report 구조 검증
- `editable-report.json`: PPTX가 이미지 덱이 아니라 편집 가능한지 검증
- `ooxml-style-report.json`: 내장 theme/master/layout/style OOXML 적용 검증
- `pattern-report.json`: 애니메이션, 빈칸 도형, 페이지 라벨, 슬라이드 밖 객체 검증
- `build-summary.json`: 최종 pass/fail 요약

## Git 공유 전 체크

```powershell
git status --short
python .codex\skills\pdf2concept-problem-pptx\scripts\self_check_skill.py `
  --report ".generated\self-check-report.json"
```

커밋에는 스킬 파일, 문서, requirements만 포함하고, 입력 PDF와 생성 PPTX는 포함하지 않습니다.
