# Version History

| Version | Date | Focus | Main Improvements |
|---|---|---|---|
| v0.1.0 | 2026-06-02 | Baseline preservation | Kept MAS V3 phase flow, PM/architect/operator split, Client-First rules, approval gate, MCP-352, workspace evidence, and handoff discipline. |
| v0.2.0 | 2026-06-02 | Claude Code and Python cleanup | Made Claude Code the only runtime, moved non-root docs into `agentic/`, removed unrelated runtime artifacts, added Python project metadata and gates. |
| v0.3.0 | 2026-06-02 | Agentic quality upgrades | Added reflection loop, ReAct action traces, JSON schemas, visual QA evidence contract, phase state gate, skill anatomy gate, relative-path gate, and version logs. |

## Current Quality Bar

- Runtime scope: Claude Code only.
- Automation language: Python.
- Path discipline: local filesystem paths inside this folder must be relative.
- Architecture target: pass the local standalone baseline in `agentic/evals/standalone-architecture-baseline.md`.
- Client-First target: use `knowledge-base/client-first-class-map.json` for Figma property to class mapping.
