# Dashboards

Aggregate views over `observability/traces/`.

## Layout

- `dashboard_latest.json` — most recent run_id's summary
- `dashboard_<date>.json` — daily roll-up
- `dashboard_week_<week>.json` — weekly trend

## Build

`python -m tools.observability.render_dashboard --run-id <run_id>`

Not yet implemented in V1; populated by reading `traces/` and writing here.
