# Agent performance

Per-agent latency / token / retry / pass-rate metrics.

## Metrics

- `p50_latency_ms`, `p95_latency_ms` per stage
- `tokens_in`, `tokens_out`, `cost_usd` per stage
- `retries` (orchestrator counter) per stage
- `pass_rate` over last N runs (rolling window)
- `score_variance` (LLM-judge over 5 reruns of the same input)

## File format

```json
{
  "agent": "extractor",
  "window": "last_20_runs",
  "p50_latency_ms": 8400,
  "p95_latency_ms": 18200,
  "tokens_in_avg": 4200,
  "tokens_out_avg": 2800,
  "retries_avg": 0.3,
  "pass_rate": 0.95,
  "score_variance": 0.04
}
```

Not yet auto-collected in V1; populated manually from `observability/traces/`.
