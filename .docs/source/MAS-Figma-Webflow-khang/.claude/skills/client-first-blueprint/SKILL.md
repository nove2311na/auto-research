---
name: client-first-blueprint
description: Produce Client-First V2 Webflow blueprints from Figma raw data using strict structure, naming, REM units, and component rules.
---

# Client-First Blueprint

## Use When

- Figma raw data is ready in `workspace/rawdata/`.
- A Webflow build needs an approved blueprint before execution.
- Client-First class naming or structure decisions are needed.

## Workflow

1. Read `knowledge-base/client-first-theory.md`.
2. Read `knowledge-base/client-first-class-map.json`.
3. Read `agentic/specs/figma-to-client-first-mapping.md`.
4. Read Figma raw data and content files.
5. Identify global components, sections, grids, flex layouts, variables, text styles, and assets.
6. Generate blueprint JSON under `workspace/blueprints/` with `class_mapping[]` entries.
7. Update `workspace/page_structure.json` with routing and section map only.
8. Confirm REM conversion and Client-First naming.
9. Return blueprint summary to PM for user approval.

## Hard Rules

- Use six-layer Client-First structure.
- Use `section_[name]`, `padding-global`, `container-[size]`, and `padding-section-[size]`.
- Use underscore only for custom child classes.
- Use REM units only.
- Do not invent a utility class when `knowledge-base/client-first-class-map.json` contains a matching rule.
- Every Figma property to class mapping needs a source and reason.
- Do not approve generic global components.

## Validation

Gatekeeper checks blueprint evidence, class map usage, required Client-First phrases, and `python scripts\gates\validate_client_first_library.py --target .`.
