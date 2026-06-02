# Rubric — 01-ingest

Per-stage application of the 8-criterion rubric.

| Criterion | Weight | What "good" looks like for 01-ingest |
|---|---|---|
| Correctness | 1.0 | v1.txt is non-empty UTF-8; no encoding errors; URL fetched = URL requested (no redirect bait) |
| Completeness | 1.0 | if 00_research/v1.json existed, ## Research Context block is appended; source URLs are present |
| Grounding | 1.0 | text matches the source (not summarized/transformed); research block is verbatim from dossier |
| Safety | 1.0 | no fetched content is >1 MB without truncation; blocked paths / .env never fetched; secrets redacted in source |
| Maintainability | 0.7 | meta is small; metadata fields are the canonical set; no surprise keys |
| Testability | 1.0 | smoke case I1 (canonical local file) reproduces; I3 (with research ref) produces the merge block |
| Cost | 0.8 | single fetch per URL; no double-fetch on retry; <5 sec for 1 MB local file |
| Reproducibility | 1.0 | same input_ref produces same v1.txt content (no time-of-day inject) |

**Thresholds:** pass >= 0.75, warn 0.55-0.75, fail < 0.55.
