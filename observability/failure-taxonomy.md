# Failure taxonomy

Canonical list of failure modes for the research-pipeline. Each = detection + handling.

## Schema (Draft-7)

```json
{
  "id": "F-NN",
  "name": "string",
  "category": "input|schema|completeness|llm_judge|path|tool|handoff|external",
  "severity": "low|medium|high|critical",
  "detected_by": "gate or agent name",
  "handling": "string (action: retry|halt|ask_human|escalate)",
  "max_retries": 3
}
```

## Failures (V1)

| ID | Name | Category | Severity | Detected by | Handling |
|---|---|---|---|---|---|
| F-01 | input-missing-required-field | input | high | completeness_gate | ask_human |
| F-02 | input-ref-malformed | input | high | completeness_gate | ask_human |
| F-03 | schema-violation | schema | high | json_schema_gate | retry |
| F-04 | schema-file-missing | schema | high | json_schema_gate | halt |
| F-05 | json-parse-error | schema | high | json_schema_gate | retry |
| F-06 | empty-artifact | completeness | high | completeness_check | halt (critic decides) |
| F-07 | llm-judge-below-threshold | llm_judge | medium | llm_judge_gate | retry |
| F-08 | llm-judge-tie | llm_judge | low | critic | pick on schema+completeness |
| F-09 | blocked-path-write | path | critical | path_safety_gate | halt + ask_human |
| F-10 | tool-not-allowed | tool | high | orchestrator hard rule | halt |
| F-11 | handoff-timeout | handoff | medium | orchestrator | resend once, then escalate |
| F-12 | upstream-missing | external | high | formatter | halt + tell @orch |
| F-13 | url-fetch-fail | external | low | ingestor | note in meta.feedback |
| F-14 | mermaid-syntax-error | completeness | medium | llm_judge | retry |
| F-15 | orchestrator-self-validate | handoff | critical | hard rule | halt (forbidden) |
| F-16 | manifest-winner-mismatch | schema | medium | manifest_consistency_gate | re-pick |
| F-17 | overrule-pass | handoff | critical | critic hard rule | halt (forbidden) |
| F-18 | underrule-fail | handoff | critical | critic hard rule | halt (forbidden) |
| F-19 | retries-exhausted | handoff | high | orchestrator | halt + notify |
| F-20 | meta-not-written | completeness | high | validator | nudge stage agent |
