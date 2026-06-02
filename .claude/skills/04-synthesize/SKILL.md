---
name: 04-synthesize
description: >
  Turns 03_analyze into a coherent narrative with insights, TL;DR, Mermaid
  diagrams (>=2, at least one flowchart and one mindmap), and theses (>=2).
  Use when the orchestrator hands off to the synthesizer; the formatter will
  polish the final report.
---

# Skill 04 — Synthesize

## Identity
- Stage id: `04_synthesize`
- Owning agent: `synthesizer`
- Schema: `schemas/04_synthesize.json` (required: `summary`, `insights`, `narrative`, `diagrams`, `theses`)
- Output format: `json`
- `max_options`: 1, `max_retries`: 3

## Input schema
| Field | Type | Required | Source |
|---|---|---|---|
| `input_id` | string (8 hex) | yes | hcom message from `@orch` |
| `03_analyze/v1.json` | file path | yes (read end-to-end) | upstream artifact |
| `02_extract/v1.json` | file path | yes (for cross-reference to facts) | upstream artifact |
| `00_research/v1.json` | file path | optional (for `key_findings` in thesis evidence) | upstream artifact (if 00_research ran) |

## Process (see `skill.json#process` for the structured form)

1. **(LLM)** Read `03_analyze/v1.json`, `02_extract/v1.json`, optionally `00_research/v1.json`.
2. **(LLM)** Form a mental model: "what is this source about, what's the most important takeaway?"
3. **(LLM)** Compose the artifact matching `schemas/04_synthesize.json`:
   - `summary`: 1-3 sentence TL;DR. Must stand alone. (maxLength: 1000)
   - `insights[]`: 3-7 distinct insights. Each has `insight`, `grounding` (which theme/gap/contradiction from `03_analyze`), `novelty` (high/medium/low).
   - `narrative`: 1-3 paragraph connected piece.
   - `diagrams[]`: **2-5** of mixed types. At minimum one `flowchart` and one `mindmap`.
   - `theses[]`: **2-5** synthesized positions. Each has `statement`, `evidence[]`, `counterarguments[]`, `confidence`.
4. **(deterministic)** Write `v1.json` + `v1.meta.json` (validation: pending).
5. **(deterministic)** Ping `@critic`.

### Diagram types (enum)
`flowchart` | `sequence` | `mindmap` | `graph` | `class` | `state` | `concept`

**Mermaid code rule:** `code` field is **raw Mermaid syntax WITHOUT the ` ```mermaid ` wrapper** — the formatter adds it.

### Thesis & Pre-Rebuttal Rule (Quy tắc Tự Phản Biện Chống Bác Bỏ)
- `evidence[]`: 2-5, drawn from `02_extract.facts[]` or `00_research.key_findings[]` (not invented)
- `counterarguments[]`: 1-3, honestly engaged (not strawmen)
- `confidence`: high/medium/low
- **Self-Rebuttal Check**: Trước khi xuất kết quả, bạn phải chủ động đóng vai một Reviewer khó tính để "soi" kỹ các luận điểm (`theses`) của mình. Hãy tự phản biện chính mình để tìm ra kẽ hở lớn nhất (ví dụ: diễn đạt quá đà/overclaim, thiếu bằng chứng thực tế, lập luận nhảy cóc), sau đó viết lại luận điểm và bổ sung bằng chứng để vá các lỗ hổng đó ngay lập tức. Đảm bảo bài viết có độ tin cậy khoa học cao nhất trước khi gửi cho Critic.

## Output schema (artifact template)
See `skill.json#output_schema` for the JSON form. Real example: `scripts/smoke_v2.py:108-132` (1 flowchart + 1 mindmap + 2 theses).

## Self-check (see `skill.json#self_check` for the full numbered list)
- `summary` ≤ 1000 chars, stands alone
- `insights[]` has 3-7 entries; each grounded in a theme/gap/contradiction
- `narrative` reads as one piece (not 5 stapled paragraphs)
- `diagrams[]` has ≥2 entries; ≥1 `flowchart` AND ≥1 `mindmap`
- Diagram `code` is Mermaid syntax WITHOUT the wrapper
- `theses[]` has ≥2 entries; evidence drawn from upstream; counterarguments honestly engaged
- No invented facts (all trace to `02_extract` or `00_research`)

## Validation
- Schema + completeness + LLM-judge
- Common failure: `diagrams` < 2 or no `flowchart`/`mindmap` → add diagrams
- Common failure: `theses` < 2 → add another thesis
- Common failure: Mermaid syntax errors → fix; critic's LLM-judge will catch

## Source
Full spec: `.docs/agentic/skills/04-synthesize.md`. JSON form: `.claude/skills/04-synthesize/skill.json`. Real example: `scripts/smoke_v2.py:108-132`.
