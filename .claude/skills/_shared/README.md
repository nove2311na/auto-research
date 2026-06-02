# Shared skill helpers

Cross-skill fixtures, scripts, and templates used by all 7 stage skills.

## Structure

```
_shared/
├── fixtures/
│   ├── qec-input.txt          # canonical sample source text (QEC dossier)
│   ├── qec-input.empty.txt    # empty input boundary
│   ├── qec-input.huge.txt     # >50K token boundary (truncate)
│   └── qec-input.url.txt      # URL fetch input
├── scripts/
│   ├── run_eval_case.sh       # run a single eval-case against the skill
│   ├── self_check.sh          # run a v1.json through the self_check list
│   └── score_rubric.sh        # apply 8-criterion rubric, emit scorecard
└── templates/
    ├── v1.meta.json.template  # the canonical meta block (producer, validation pending)
    └── input_id.README.md     # how to derive input_id from a path/URL/topic
```

## Conventions

- One `input_id` per pipeline run. Derive from `hashlib.sha1(input_ref.encode()).hexdigest()[:8]`.
- One `v<N>.<ext>` per artifact version. `v1.json` is the first attempt; retries write `v2.json`, etc.
- Every `v<N>.<ext>` has a sibling `v<N>.meta.json` with the canonical block from `templates/v1.meta.json.template`.
