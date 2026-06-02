---
name: mcp-352-webflow-build
description: Execute approved Webflow builds using native element operations and the MCP-352 micro-chunking rule.
---

# MCP-352 Webflow Build

## Use When

- The blueprint is approved by the user.
- Webflow target site/page is confirmed.
- Operator is executing Phase 2.

## Workflow

1. Confirm approved blueprint path.
2. Confirm Webflow site/page IDs.
3. Take a pre-build snapshot or state scan.
4. Build using max 3 nesting levels per turn.
5. Limit each turn to max 5 Webflow actions.
6. Verify element tree after every 2 successful actions.
7. Log each action in `workspace/state.json`.
8. Stop at verification boundaries or tool failures.

## Forbidden

- No `whtml_builder`.
- No silent page creation.
- No external writes without target confirmation.
- No real asset upload by default.

## Validation

The QA loop must inspect actual Webflow state before final approval.

