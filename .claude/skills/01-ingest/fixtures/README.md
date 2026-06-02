# Fixtures for 01-ingest

| File | Shape | Used by eval-case |
|---|---|---|
| `path.canonical.txt` | Real local file path | I1 |
| `url.404.txt` | https://example.com/does-not-exist | I2 |
| `with-research-ref.txt` | URL + 00_research/v1.json expected present | I3 |
| `large.txt` | Triggers 1 MB truncation | I4 |
| `expected_output.txt` | The merged v1.txt for the canonical input | I1, I3 |
| `expected_meta.json` | Canonical meta block (with research_ref) | I1, I3 |
