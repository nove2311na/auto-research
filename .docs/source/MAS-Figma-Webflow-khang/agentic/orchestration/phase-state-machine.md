# Phase State Machine

The PM controls phase movement. Workers can propose state changes, but only the PM records phase decisions.

## States

| State | Entry Condition | Exit Condition |
|---|---|---|
| `phase_0_setup_audit` | New request or resumed workspace. | Workspace, handoff, MCP readiness, and target evidence are known. |
| `phase_1_blueprint` | Figma source or source substitute is accepted. | Blueprint exists and user approval is recorded. |
| `phase_2_webflow_build` | User approval exists for a specific blueprint version. | Webflow action log exists and QA is ready. |
| `phase_3_qa_loop` | Build or fix action is complete. | QA verdict is `[APPROVED]` or unresolved blockers are documented. |
| `handoff_closeout` | Phase completes or session ends. | `agentic/memory/session-handoff.md` is updated. |

## Allowed Transitions

```text
phase_0_setup_audit -> phase_1_blueprint
phase_1_blueprint -> phase_2_webflow_build
phase_2_webflow_build -> phase_3_qa_loop
phase_3_qa_loop -> phase_2_webflow_build
phase_3_qa_loop -> handoff_closeout
any_phase -> handoff_closeout
```

## Approval Rule

`phase_1_blueprint -> phase_2_webflow_build` is blocked unless `workspace/state.json` contains an approval entry with:

- `type`: `approval`
- `phase`: `phase_1_blueprint`
- `artifact`: the approved blueprint path
- `message`: contains `Approved`
- `approver`: `user`

## ReAct Rule

Every Webflow mutation in `phase_2_webflow_build` must record:

- `reason`
- `action`
- `observation`
- `next_decision`

This keeps tool use auditable and prevents build steps from becoming unexplained mutations.

