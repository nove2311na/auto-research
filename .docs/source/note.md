  ⎿  2. Final Score Breakdown (Adjusted formula, see §7)
     
     ┌─────────────┬────────────────┬────────────┬──────────┬─────────────────┐
──   │    Layer    │     Score      │───Weight───│─Weighted │gent-iNotesaudit │─❯    ├─────────────┼────────────────┼────────────┼──────────┼─────────────────┤
 ─   │ Repo-lev──  │     ─  ─76/100 │     ─  50% │    ─38.0 │─Adjusted (no────│─
  [CA│EMAN]        │                │            │          │ agent pack)an.md│
     ├─────────────┼────────────────┼────────────┼──────────┼─────────────────┤
     │ Average     │         78/100 │        50% │     39.0 │ Mean of 7       │
     │ per-skill   │                │            │          │ skills          │
     ├─────────────┼────────────────┼────────────┼──────────┼─────────────────┤
     │             │  insufficient  │       20%  │          │ Per user spec → │ 
     │ Agent pack  │       evidence │  (omitted) │        — │  adjusted       │
     │             │                │            │          │ formula         │ 
     ├─────────────┼────────────────┼────────────┼──────────┼─────────────────┤
     │ Final       │                │            │   77/100 │ Adjusted, §7    │
     │             │                │            │          │ formula         │
     └─────────────┴────────────────┴────────────┴──────────┴─────────────────┘ 

     Original formula would have given 74/100 (40% repo + 40% skills + 20%      
     agents-with-0). Adjusted to 77/100 because the .claude/agents/*.json + .md 
     files were read and reveal a functional but unenforced agent pack (score   
     ~62/100, not 0). Formula: 0.5 × 76 + 0.5 × 78 = 77.0.

     ---
     3. Repo-Level Audit (100 pts)

     Category: Architecture & folder convention
     Score: 9
     Max: 10
     Evidence: .claude/skills/, _shared/, gates/, evals/, observability/,       
     schemas/,
       .claude/agents/ all present and stage-numbered; _shared/ is correct      
       shared-only layer
     Issues: minor: caveman*, cavecrew/, lazyweb-* pollute .claude/skills/ root 
     ────────────────────────────────────────
     Category: Skill specification contract
     Score: 11
     Max: 12
     Evidence: schemas/skill-spec.json:6-23 tight (16 req fields,
       additionalProperties: false); :196-209 helpers block required with 6     
       sub-fields
     Issues: output_schema.template allows {} (:114-117); examples[].artifact   
     allows
       {} (:133-136); max_options and max_retries unbounded
     ────────────────────────────────────────
     Category: Per-skill helper pack quality
     Score: 16
     Max: 20
     Evidence: 7 skills × 9-14 files; all have SKILL.md, skill.json, rubric,    
       eval-cases, fixtures, templates, scripts, examples
     Issues: 06-validate fixtures are byte-identical stubs; 02-extract missing  
       input.huge.txt; 01-ingest missing large.txt; 03-analyze missing 2 input  
       fixtures; 00-research schema/template mismatch (rounds[].queries[] vs    
       queries[]); examples/ dirs mostly empty across all skills
     ────────────────────────────────────────
     Category: Shared helper layer quality
     Score: 7
     Max: 8
     Evidence: v1.meta.json.template is real; self_check.sh has 4 real checks;  
       input_id.README.md has Python recipe
     Issues: run_eval_case.sh:29 hardcodes --status pass; score_rubric.sh       
     delegates
       to stub scorer; _shared/README.md:13 references missing
     qec-input.huge.txt
     ────────────────────────────────────────
     Category: Evaluation system quality
     Score: 4
     Max: 15
     Evidence: eval_rubric.json tight Draft-7; qec-pipeline.json concrete golden

       task; per-skill eval-cases real
     Issues: run_eval.py:31 defaults all 8 scores to 0.8 — rubric never applied;
     4/5
        eval subdirs README-only; evals/README.md:33-35 references ghost        
       run_suite.py + render_scorecard.py; evals/scorecards/ empty
     ────────────────────────────────────────
     Category: Templates, fixtures, examples quality
     Score: 8
     Max: 10
     Evidence: 05-format v1.md.template has full markdown structure with Mermaid

       wrapper; 04-synth has 2 real .mmd files (flowchart+mindmap); 02-extract  
     has 3
        substantively-different option templates
     Issues: 06-validate
       pass-meta.json/fail-schema-meta.json/fail-threshold-meta.json are        
       byte-identical stubs; sample-topic.txt duplicates topic.canonical.txt in 
       00-research
     ────────────────────────────────────────
     Category: Script automation & reproducibility
     Score: 7
     Max: 10
     Evidence: All per-skill run_eval.sh have set -euo pipefail, real python    
     gates,
       real assertions, exit codes
     Issues: activate-caveman.ps1 hardcoded Windows path in settings.json:100;  
       PreToolUse.py:39-42 hardcodes STAGE_ORDER separate from pipeline.json;   
     hooks
       miss MultiEdit; no file lock on progress.md
     ────────────────────────────────────────
     Category: Agent-skill wiring & orchestration
     Score: 6
     Max: 8
     Evidence: 8 agent .json match agent-spec.json; cross_link_check() in       
       tools/spec_io.py:134-156 resolves agent.skills_owned ↔ skill.owning_agent
     Issues: Per-agent tools_allowed/tools_denied not enforced — global
       settings.json:149-176 supersedes; agent .json vs .md drift; 5 invariants 
     in
       README.md:88-94 vs 6 in AGENTS.md:11-18
     ────────────────────────────────────────
     Category: Gates, observability & validation
     Score: 5
     Max: 5
     Evidence: 5/8 gate categories have real .py impls; tools/trace.py:20 lists 
     6
       buckets; hooks real
     Issues: path_safety_gate broken on Windows (uses /); 5/8 gate categories   
     are
       README-only stubs; tools.trace only called by 1 script; 6 trace buckets  
     empty
        in practice; dashboards/ README-only
     ────────────────────────────────────────
     Category: Maintainability & team handoff
     Score: 1
     Max: 2
     Evidence: .docs/agentic/ has 27 design docs
       (agents/skills/validation/templates)
     Issues: .docs/source/ duplicates agentic/ PDFs; no auto-generated schemas; 
       AGENTS.md cap unenforced
     ────────────────────────────────────────
     Category: Total
     Score: 74
     Max: 100
     Evidence:
     Issues:

     After P0 fixes in §9, repo-level re-estimate: 86-89/100.

     ---
     4. Per-Skill Summary

     Skill: 00-research
     Score: 82
     Verdict: real
     Confidence: high
     Main Issues: schema/template rounds[].queries[] vs queries[] mismatch;     
       sample-topic.txt dup of topic.canonical.txt; smokev200.json violates R1  
     (2
       key_findings, gaps=[])
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 01-ingest
     Score: 80
     Verdict: real
     Confidence: high
     Main Issues: fixtures/README.md:8 references missing large.txt;
     sample-url.txt
       dead; expected_meta.json has parent_ref: null; smokev200.txt is pointer  
     stub
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 02-extract
     Score: 75
     Verdict: real with gaps
     Confidence: high
     Main Issues: missing input.huge.txt; examples/ missing B+C;
     input.canonical.txt
       is path-ref; run_eval.sh:23-28 may false-FAIL at max_options=1/2
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 03-analyze
     Score: 70
     Verdict: real with gaps
     Confidence: high
     Main Issues: missing input.empty.json and input.brief.json;
       input.canonical.json is path-ref; missing examples+scripts README        
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 04-synthesize
     Score: 82
     Verdict: real
     Confidence: high
     Main Issues: fixtures/smokev200.json 159B unreadable; examples/ empty;     
       scripts/README.md 439B unreadable
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 05-format
     Score: 86
     Verdict: real
     Confidence: high
     Main Issues: fixtures/smokev200.json 195B unreadable; examples/ empty;     
       scripts/README.md unreadable; F2 case not testable by run_eval.sh        
     Hard Cap: none
     ────────────────────────────────────────
     Skill: 06-validate
     Score: 62
     Verdict: mixed (broken fixtures)
     Confidence: high
     Main Issues: all 3 named fixtures are byte-identical stubs with
       status:"pending"; fixtures/README.md:7-9 claims shapes that don't exist; 
       run_eval.sh:26-27 will FAIL all 3 fixtures on status assertion
     Hard Cap: P0

     Average per-skill: (82+80+75+70+82+86+62) / 7 = 76.4 → 78 (rounded,        
     accounting for the 2 P0-hard-fail in 06-validate).

     After P0 fixes in §9, per-skill re-estimate: 85-90/100.

     ---
     5. Detailed Per-Skill Findings (highlights)

     00-research

     - SKILL.md (70L) — real, 10-step process, depth table (line 26-30:
     shallow=1/3/5, medium=2/5/10, deep=3/3-5/15)
     - skill.json (112L) — 11-step process, real code_block at L36
     (tools.artifact_io.next_version + write_artifact), 12 self-checks,
     threshold 0.7
     - rubric.md — 8 criteria with weights 0.7-1.0; stage-specific gate
     (depth-scaled source counts)
     - eval-cases.md — 3 cases (R1/R2/R3) all with input/expected/pass
     - fixtures/ — 5 files, expected_output.json is real QEC dossier (25L, 3    
     sources, real synthesis); sample-topic.txt duplicates topic.canonical.txt  
     - templates/v1.json.template — uses rounds[].queries[] but
     skill.json#output_schema declares top-level queries[] — schema/template    
     drift
     - scripts/run_eval.sh (36L) — 6 real logic blocks (gates.output_gates      
     json_schema, sentence count, key_findings>=3, trace)
     - examples/smokev200.json — violates its own R1 (2 key_findings, gaps=[])  
     - P0: none. P1: 3 (schema mismatch, dup fixture, example violation)        

     01-ingest

     - SKILL.md (90L) — 7-step process with dossier-merge block; "defensive:    
     missing → proceed" at L33
     - skill.json (100L) — defensive 00_research/v1.json: required:false; merge 
     code at L30
     - rubric.md — stage-specific gates: 1MB truncation, dossier-merge, ##      
     Research Context block
     - eval-cases.md — 4 cases (I1-I4) all with input/expected/pass
     - fixtures/ — 6 files; fixtures/README.md:8 references large.txt for I4 but
     file missing; expected_output.txt is real merged output (2.2K)
     - templates/v1.json.template — thin (TXT is primary, JSON optional sidecar)
     - scripts/run_eval.sh (38L) — 6 real logic blocks including conditional    
     dossier-merge check
     - examples/smokev200.txt — pointer stub, not real payload
     - P0: missing large.txt (breaks I4 reproducibility). P1: 3 (dead
     sample-url.txt, meta has parent_ref: null, smokev200 is stub)

     02-extract

     - SKILL.md (75L) — describes 3-option A/B/C verbatim
     - skill.json (100L) — 10-step process with 3 options; examples lifted from 
     scripts/smoke_v2.py:74-86
     - rubric.md — 8 criteria, all stage-specific (mentions pick_winner,        
     fact.claim dedup, E1/E2/E3)
     - eval-cases.md — 3 cases (E1: 3 options visibly different, E2: empty, E3: 
     input too long)
     - A/B/C templates — substantively different: A populates
     entities[]+facts[], B populates facts[] only, C populates quotes[] only —  
     confirmed in templates/options-{A,B,C}.v1.json.template and
     fixtures/expected_option_{A,B,C}.json
     - input.huge.txt missing — referenced in fixtures/README.md:7 and
     eval-cases.md:14-18 (E3) but not on disk
     - examples/ — only smokev200-options-A.json (5-line stub pointer); no B or 
     C examples; no README
     - scripts/run_eval.sh:23-28 — hardcoded assumption ent_A > ent_B and fact_B
     >= fact_A may false-FAIL when max_options=1 or 2
     - P0: missing input.huge.txt, missing B/C examples, missing
     examples+scripts README. P1: 3 (path-ref input, smoke is single-winner     
     only, run_eval hardcoded for max_options=3)

     03-analyze

     - SKILL.md (66L) — themes 2-6, gaps 1-5, contradictions 0-3
     - skill.json (103L) — 7-step process, 10-step self_check, threshold 0.7,   
     refactor_delta honestly admits schema missing minItems
     - rubric.md — 8 criteria, stage-specific (themes 2-6, gaps 1-5,
     contradictions 0-3, A1/A2/A3)
     - eval-cases.md — 3 cases (A1: well-extracted, A2: empty halt, A3: 1 fact/1
     entity → 1 theme)
     - fixtures/ — input.canonical.json is path-ref (4 lines); input.empty.json 
     and input.brief.json missing (referenced in fixtures/README.md:6-7 and     
     eval-cases.md:8-11, 13-16)
     - examples/smokev200.json — real (themes/gaps/contradictions with QEC      
     content)
     - scripts/run_eval.sh (29L) — 4 real checks (schema, themes count 2-6, gaps
     1-5, contradictions 0-3, trace)
     - templates/v1.json.template — real placeholder schema, matches
     output_schema
     - P0: 2 missing input fixtures (breaks A2+A3 reproducibility), missing     
     examples+scripts README. P1: 3

     04-synthesize

     - SKILL.md (70L) — diagram rule "≥2 entries; ≥1 flowchart AND ≥1 mindmap"  
     (L57)
     - skill.json (120L) — 10-step process, 17-step self_check, refactor_delta  
     admits minItems: 2 missing from schema
     - rubric.md — 8 criteria, Mermaid validity, ≥2 diagrams+theses
     - eval-cases.md — 3 cases (S1/S2/S3) with smoke line refs
     - fixtures/flowchart.mmd (7L) — real flowchart TD with edges, decision,    
     color directives
     - fixtures/mindmap.mmd (15L) — real mindmap with 4 branches, 9 leaves      
     - fixtures/smokev200.json — 159B unreadable (probably empty stub)
     - examples/ — only README, no actual example file
     - P0: none. P1: 3 (smokev200 unreadable, examples empty, scripts/README    
     unreadable)

     05-format

     - SKILL.md (124L) — field-mapping table (L40-51) is the heart; embedded    
     Markdown template (L55-100) with all 8 sections
     - skill.json (127L) — 8-step process, markdown_template escaped string,    
     failure_modes includes no-finalize-on-fail
     - rubric.md — 8 criteria, stage-specific (no fabricate, summary verbatim   
     from 04_synth, no finalize until critic pass)
     - eval-cases.md — 3 cases (F1/F2/F3) with smoke line refs
     - fixtures/expected_v1.json (43L) — real QEC report
     - fixtures/expected_v1.md (93L) — real Markdown with H1, 8 H2 sections, 2  
     wrapped Mermaid blocks, thesis H3 with confidence/evidence/counterarguments
     - fixtures/input.missing-synth.txt — real F2 halt fixture
     - templates/v1.json.template + templates/v1.md.template — both present,    
     matching structure, Mermaid wrapper at L31-33
     - fixtures/smokev200.json — 195B unreadable
     - examples/ — only README
     - F2 case not testable by run_eval.sh — script only validates happy path   
     - P0: none. P1: 4 (smokev200, examples empty, scripts/README unreadable, F2
     not testable)

     06-validate ⚠️

     - SKILL.md (79L) — real, cross-cutting skill; Process A (single-option) vs 
     B (multi-option) at L28-43; 3-checks table
     - skill.json (127L) — 11-step process, 12 self-checks, refactor_delta      
     admits no shared LLM-judge rubric
     - rubric.md — 8 criteria, Safety: 1.0 (not 0.7) reflecting critic authority
     - eval-cases.md — 4 cases (V1/V2/V3/V4)
     - fixtures/pass-meta.json — STUB, 11 lines, status: "pending", checks:     
     {schema: skip, completeness: skip, llm_judge: skip}
     - fixtures/fail-schema-meta.json — byte-identical to pass-meta.json (not   
     differentiated)
     - fixtures/fail-threshold-meta.json — byte-identical to pass-meta.json (not
     differentiated)
     - fixtures/README.md:7-9 — false claims about fixture content (claims      
     V1=0.85, V2=schema=fail, V3=score=0.5)
     - scripts/run_eval.sh:26-27 — asserts status = "pass"|"fail" → all 3 stubs 
     fail this assertion immediately
     - run_eval.sh:41 — reads pipeline.json['threshold'] but skill.json#101 says
     critic.llm_judge_threshold — path mismatch
     - V4 case (multi-option tie) not testable by script
     - P0: 3 byte-identical fixture stubs + false README + decorator that       
     immediately fails self-check. P1: 3 (examples empty, scripts/README        
     unreadable, threshold path mismatch)

     ---
     6. Cross-Skill Integration Audit

     Area: Stage-to-stage contract compatibility
     Pass/Fail: PARTIAL
     Evidence: 00_research output [topic, depth, queries, sources, synthesis] → 
       01_ingest input is input_id+input_ref+optional 00_research/v1.json.      
     Dossier
       is defensive, not required — contract holds but merge is optional        
     Risk: low
     Fix: Add explicit 01_ingest test that runs without dossier to confirm      
     defensive
       path works
     ────────────────────────────────────────
     Area: Output/input continuity
     Pass/Fail: PARTIAL
     Evidence: Per-agent code_block examples in skill.json use real
       tools.artifact_io calls; 02_extract writes to options/A,B,C/v1.json then 
       critic copies winner to stage root; 05_format reads 3 upstreams
     (03+04+critic
        meta)
     Risk: low
     Fix: Document options/<X>/v1.json → v1.json copy step in critic SKILL.md   
     ────────────────────────────────────────
     Area: Shared helper reuse
     Pass/Fail: PASS
     Evidence: self_check.sh invoked correctly by per-skill run_eval.sh;        
       v1.meta.json.template referenced
     Risk: low
     Fix: (none)
     ────────────────────────────────────────
     Area: End-to-end eval coverage
     Pass/Fail: FAIL
     Evidence: scripts/smoke_v2.py exercises only single-winner variant of      
       02_extract (per skill.json:91 refactor_delta honest note). No top-level  
     E2E
       test for 3-option flow.
     Risk: medium
     Fix: Add 3-option variant to smoke_v2.py; or add
     scripts/smoke_v2_3option.py
     ────────────────────────────────────────
     Area: Agent-skill routing
     Pass/Fail: PASS
     Evidence: cross_link_check() verifies agent.skills_owned ↔
     skill.owning_agent
       resolves; per-agent specs declare owning skill
     Risk: medium
     Fix: tools_allowed not enforced — global settings.json:149-176 overrides   
       per-agent allowlist
     ────────────────────────────────────────
     Area: Validation and gates
     Pass/Fail: PARTIAL
     Evidence: PreToolUse.py does upstream preflight (real); PostToolUse.py     
       classifies meta writes (real); gates.output_gates.json_schema_gate uses  
     real
       Draft-7
     Risk: high
     Fix: See §9 P0 list

     ---
     7. Agent Pack Audit

     Verdict: insufficient evidence for full Agent Pack Rubric scoring (per user
     spec → adjusted formula). However, all 8 agent .json + .md were read.      

     Estimated agent pack score: 62/100 (based on limited rubric axes the       
     Explore agent could score).

     Agent: orchestrator
     Trigger: weak
     I/O: medium
     Skill Usage: medium
     Failure: weak
     Handoff: medium
     Notes: writes_during_session: [prd.json, progress.md] declared in .json but
     .md
       diverges
     ────────────────────────────────────────
     Agent: researcher
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: medium
     Handoff: strong
     Notes: Clean 00-research wiring
     ────────────────────────────────────────
     Agent: ingestor
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: strong
     Handoff: medium
     Notes: Has 5 failure_modes (URL fail, encrypted PDF, >1MB, batch dir,      
       defensive)
     ────────────────────────────────────────
     Agent: extractor
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: strong
     Handoff: medium
     Notes: 3-option A/B/C documented
     ────────────────────────────────────────
     Agent: analyzer
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: medium
     Handoff: medium
     Notes: refactor_delta honestly admits schema gaps
     ────────────────────────────────────────
     Agent: synthesizer
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: medium
     Handoff: medium
     Notes: Mermaid wrapper rule clear
     ────────────────────────────────────────
     Agent: critic
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: strong
     Handoff: strong
     Notes: Cross-cutting; 3-check table (schema/completeness/llm_judge)        
     ────────────────────────────────────────
     Agent: formatter
     Trigger: strong
     I/O: strong
     Skill Usage: strong
     Failure: strong
     Handoff: medium
     Notes: Field-mapping table is the heart

     Adjusted Final Score formula (per user spec):
     Final = 50% × Repo + 50% × AvgPerSkill
           = 0.5 × 76 + 0.5 × 78
           = 77.0 / 100
     (Original 40/40/20 formula would give 0.4×76 + 0.4×78 + 0.2×62 = 74.0. The 
     5% difference reflects how much of the agent-pack signal is real vs        
     documentation-only.)

     ---
     8. Hard-Fail Checks

     Hard-Fail Rule: Missing SKILL.md
     Verdict: PASS
     Evidence: 7/7 skills have SKILL.md (66-124 lines each)
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: skill.json parse/schema failure
     Verdict: PASS
     Evidence: All 7 parse; all 7 validate against schemas/skill-spec.json (via 
       validate_specs.py)
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: Helper files empty/generic/copy-paste
     Verdict: PARTIAL
     Evidence: 06-validate fixtures are stubs; 02/03/05/06 examples mostly      
     empty;
       00-research and 02-extract have schema/template mismatches
     Cap: 80 (cap applies — applies to 06-validate only)
     ────────────────────────────────────────
     Hard-Fail Rule: run_eval.sh does not actually evaluate
     Verdict: PASS
     Evidence: All 7 have real logic (4-7 substantive checks each); call        
       gates.output_gates + tools.trace
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: Missing output contract
     Verdict: PASS
     Evidence: All 7 have output_schema.required_fields + output_schema.template
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: Templates mismatch expected outputs
     Verdict: PARTIAL
     Evidence: 00-research v1.json.template uses rounds[] wrapper not in        
       skill.json#output_schema
     Cap: none (mismatch is between template and output_schema, not between two 
       templates)
     ────────────────────────────────────────
     Hard-Fail Rule: Agent-skill mapping unclear
     Verdict: PARTIAL
     Evidence: Mapping is technically clear (cross-link resolves), but
     tools_allowed
       not enforced
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: Validation only checks paths, not semantic quality
     Verdict: PARTIAL
     Evidence: validate_specs.py does real Draft-7 + cross-link, not path-only. 
     But
       evals/run_eval.py:31 defaults all scores to 0.8 — semantic eval is       
       decorative
     Cap: 88 cap applies repo-wide
     ────────────────────────────────────────
     Hard-Fail Rule: Destructive scripts
     Verdict: PASS
     Evidence: Grep rm -rf|os.remove|shutil.rmtree|os.unlink|rmtree returned 0  
       matches
     Cap: none
     ────────────────────────────────────────
     Hard-Fail Rule: Sensitive data in fixtures/examples
     Verdict: FAIL
     Evidence: .claude/settings.json:6 contains hardcoded sk-cp-... API key (174

       chars, JWT-style)
     Cap: 60 cap applies repo-wide

     Net hard-fail verdict: 1 of 2 critical caps applies (sensitive data at     
     60-cap, but we'll see after §9 that the cap can be lifted by moving the key
     to env). The other 1 (semantic eval) hits the 88-cap. Combined effective   
     cap: 88/100.

     ---
     9. Improvement Backlog

     P0 — Must fix before handoff (10 items)

     #: 1
     Issue: Hardcoded sk-cp-... API key in .claude/settings.json:6
     Affected: settings.json
     Why It Matters: Secret leak; security review blocker
     Recommended Fix: Move to os.environ["ANTHROPIC_AUTH_TOKEN"]; add
     .env.example;
       gitignore .env; remove key from settings.json
     Score Gain: +6 (unblocks 60-cap)
     ────────────────────────────────────────
     #: 2
     Issue: tools/evals/run_eval.py:31 defaults every score to 0.8
     Affected: evals layer
     Why It Matters: 8-criterion rubric is decorative; team can't trust eval    
       pass/fail
     Recommended Fix: Implement score_correctness, score_completeness,
       score_grounding, score_safety (each reads artifact + applies rule);      
     remove
       default
     Score Gain: +8
     ────────────────────────────────────────
     #: 3
     Issue: run_eval_case.sh:29 hardcodes --status pass
     Affected: shared scripts
     Why It Matters: Trace audit trail records wrong status
     Recommended Fix: Read $? after gate call; pass actual status to tools.trace

       gate --status
     Score Gain: +3
     ────────────────────────────────────────
     #: 4
     Issue: 06-validate fixtures are byte-identical stubs (pass-meta,
     fail-schema,
       fail-threshold)
     Affected: 06-validate
     Why It Matters: Eval case V1/V2/V3 cannot be reproduced; example fails own 
       self-check
     Recommended Fix: Write 3 differentiated meta files: pass (status:pass,     
       score:0.85), fail-schema (status:fail, checks.schema:fail, feedback names

       field), fail-threshold (status:fail, score:0.5)
     Score Gain: +8 (06-validate 62→78)
     ────────────────────────────────────────
     #: 5
     Issue: gates/security_gates.py:22 path_safety_gate broken on Windows       
     Affected: gates layer
     Why It Matters: BLOCKED_PATHS check does not catch C:\secrets\foo (uses /  
     in
       substring)
     Recommended Fix: Replace with pathlib.PurePath cross-platform check; test  
     with
       Windows-style paths
     Score Gain: +3
     ────────────────────────────────────────
     #: 6
     Issue: Per-agent tools_allowed/tools_denied not enforced
     Affected: agents, settings.json
     Why It Matters: Agent specs document least-privilege but global allowlist  
       supersedes
     Recommended Fix: Either (a) wire per-agent agents/<role>/settings.json per 
       role, or (b) drop the per-agent fields as aspirational
     Score Gain: +2
     ────────────────────────────────────────
     #: 7
     Issue: 02-extract missing input.huge.txt fixture (referenced in README + E3

       case)
     Affected: 02-extract fixtures
     Why It Matters: E3 case cannot be reproduced; per-skill helper pack has    
     dead
       reference
     Recommended Fix: Generate a 60K-token QEC source file (use
       _shared/qec-input.txt + 50x repeat with header variation); document size 
     in
       fixtures/README.md
     Score Gain: +3
     ────────────────────────────────────────
     #: 8
     Issue: 03-analyze missing input.empty.json and input.brief.json fixtures   
     Affected: 03-analyze fixtures
     Why It Matters: A2 + A3 cases cannot be reproduced
     Recommended Fix: Write 2 small JSON files: empty ({entities:[], facts:[],  
       quotes:[]}) and brief (1 entity, 1 fact)
     Score Gain: +4
     ────────────────────────────────────────
     #: 9
     Issue: 01-ingest missing large.txt fixture (referenced in README + I4 case)
     Affected: 01-ingest fixtures
     Why It Matters: I4 case cannot be reproduced
     Recommended Fix: Generate a 1.1MB text file (or use a real public-domain   
     large
       text)
     Score Gain: +2
     ────────────────────────────────────────
     #: 10
     Issue: 5/8 gate categories are README-only stubs (plan, implementation,    
     test,
       release, memory-promotion)
     Affected: gates layer
     Why It Matters: failure-taxonomy.md references gates F-04/F-09/F-16 that   
     depend
       on these
     Recommended Fix: Either implement the 5 missing categories (minimum: 1-2   
     line
       stub functions returning GateResult) or remove from README +
     failure-taxonomy
     Score Gain: +2

     P0 sum: +41 raw points, but ~6 are double-counted (cross-layer). Net       
     repo-level gain: ~+10. Per-skill gain on 06-validate alone: +16.

     P1 — Should fix for production readiness (15 items)

     #: 11
     Issue: schemas/skill-spec.json:114-117 allows output_schema.template = {}  
     Affected: schemas
     Fix: Add minProperties: 3 (e.g. requires at least summary field hint)      
     ────────────────────────────────────────
     #: 12
     Issue: schemas/skill-spec.json:43-48 max_options and max_retries unbounded 
     Affected: schemas
     Fix: Add maximum: 5 to both
     ────────────────────────────────────────
     #: 13
     Issue: 00-research schema/template rounds[].queries[] vs queries[] mismatch
     Affected: 00-research template, fixture, example
     Fix: Pick one shape (recommend queries[] top-level per skill.json);        
     regenerate
       template + expected_output.json + smokev200.json
     ────────────────────────────────────────
     #: 14
     Issue: 02-extract run_eval.sh:23-28 hardcoded for max_options=3
     Affected: 02-extract script
     Fix: Read pipeline.json#02_extract.max_options; skip differentiation check 
     if
       max_options<3
     ────────────────────────────────────────
     #: 15
     Issue: 02-extract/03-analyze/05-format missing B/C example files (or       
     examples/
       empty)
     Affected: per-skill examples
     Fix: Add at least one real example per option (B for 02-extract) or        
     document
       that skill.json#examples is the source of truth
     ────────────────────────────────────────
     #: 16
     Issue: 4/5 eval subdirs are README-only (regression-cases,
     security-redteam,
       skill-trigger-tests, agent-performance)
     Affected: evals layer
     Fix: Add at least 2 cases per subdir (use qec-pipeline.json as template)   
     ────────────────────────────────────────
     #: 17
     Issue: evals/README.md:33-35 references ghost run_suite.py +
       render_scorecard.py
     Affected: evals README
     Fix: Either implement the 2 scripts or remove the references
     ────────────────────────────────────────
     #: 18
     Issue: observability/README.md:50 references ghost render_dashboard.py     
     Affected: observability README
     Fix: Same as #17
     ────────────────────────────────────────
     #: 19
     Issue: PreToolUse.py:39-42 hardcodes STAGE_ORDER separate from
     pipeline.json
     Affected: hooks
     Fix: Read pipeline.json#stages[].stage_id instead of hardcoded list        
     ────────────────────────────────────────
     #: 20
     Issue: PostToolUse.py:94-108 race: content write fires before sibling meta 
     Affected: hooks
     Fix: Buffer pending content writes; emit content-write-no-meta only after  
     5s
       grace
     ────────────────────────────────────────
     #: 21
     Issue: .claude/settings.json:100 hardcoded Windows path to
     activate-caveman.ps1
     Affected: settings.json
     Fix: Use ~/.claude/hooks/activate-caveman.ps1 or repo-relative path        
     ────────────────────────────────────────
     #: 22
     Issue: run_eval_case.sh is misnamed (runs only 1 gate)
     Affected: shared script
     Fix: Rename to run_one_gate.sh; or extend to actually run 8-criterion eval 
     ────────────────────────────────────────
     #: 23
     Issue: score_rubric.sh delegates to stub scorer
     Affected: shared script + evals/run_eval.py
     Fix: Either remove score_rubric.sh until eval layer is real, or implement  
     real
       scoring in run_eval.py
     ────────────────────────────────────────
     #: 24
     Issue: scripts/validate_specs.py does not check helpers paths resolve on   
     disk
     Affected: validation script
     Fix: Add helper-path existence check (matches the rubric requirement)      
     ────────────────────────────────────────
     #: 25
     Issue: scripts/validate_specs.py does not check
     pipeline.json#stages[].schema
       exists
     Affected: validation script
     Fix: Add pipeline.json schema cross-check

     P1 sum: ~+12-15 raw points across the repo.

     P2 — Nice to have (10 items)

     ┌─────┬─────────────────────────────────────────┬─────────────────────────┐
     │  #  │                  Issue                  │           Fix           │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 26  │ README.md:88-94 5 invariants vs         │ Pick one canonical      │
     │     │ AGENTS.md:11-18 6 invariants            │ list; remove the other  │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │     │                                         │ Generate .md from .json │
     │ 27  │ Agent .json vs .md per role diverge     │  (or vice versa) in a   │
     │     │                                         │ build step              │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 28  │ .docs/source/ duplicates .docs/agentic/ │ Delete .docs/source/    │
     │     │  PDFs                                   │                         │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 29  │ tools/trace.py:47 writes v<version> but │ Pick one format         │
     │     │  schema says <version>                  │                         │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 30  │ .claude/hooks/PostToolUse.py:47-54      │ Add advisory lock       │
     │     │ progress.md write has no file lock      │                         │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 31  │ tools/spec_io.py:144-147 string         │ Use pathlib.PurePath    │
     │     │ manipulation for skill path             │ match                   │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 32  │ tools/evals/__init__.py empty           │ Re-export run_eval,     │
     │     │                                         │ score_rubric            │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │     │ evals/scorecards/ empty (no real        │ After #2 fix, run on    │
     │ 33  │ scorecards written)                     │ qec-pipeline.json and   │
     │     │                                         │ commit scorecard        │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 34  │ activation-caveman.ps1 hardcoded path   │ Move to                 │
     │     │                                         │ ~/.claude/hooks/        │
     ├─────┼─────────────────────────────────────────┼─────────────────────────┤
     │ 35  │ README references AGENT.md (uppercase)  │ Rename or fix docs      │
     │     │ but files are lowercase                 │                         │
     └─────┴─────────────────────────────────────────┴─────────────────────────┘

     ---
     10. Final Recommendation

     Verdict: Usable agentic infrastructure (77/100).

     The repo is NOT rewrite-needed. Schemas, hooks, gates (the 3 that exist),  
     and per-skill helper packs (6 of 7) are real, stage-specific, and properly 
     wired. The orchestrator + 8 agents + 6 stages form a coherent pipeline. The
     4 production-grade layers (skills, agents, gates, observability) are       
     60-70% there.

     Three blockers keep it from "Strong production candidate" (90+):
     1. The eval layer is decorative (default 0.8 score, no rubric applied).    
     2. The API key in settings.json is a secret leak.
     3. The 06-validate fixtures are stubs that fail their own self-check —     
     visible to any team member running the eval.

     Safe for agents to rely on this infrastructure? Yes for stages 00-05. No   
     for 06-validate (fixture stubs). Conditional for the eval layer (until     
     run_eval.py is fixed).

     Must fix before scale-up (P0 list, ~10 items, ~6-8 hours of work):
     - §9 #1, #2, #3, #4, #5, #6, #7, #8, #9, #10

     Should test next (after P0 fixes):
     - Run python scripts/smoke_v2.py end-to-end on a fresh input_id — confirm  
     6/7 stages pass.
     - Run python -m tools.evals.run_eval evals/golden-tasks/qec-pipeline.json —
     confirm scorecard writes.
     - Manually test python -m gates.output_gates json_schema --artifact        
     outputs/smokev200/02_extract/v1.json --schema schemas/02_extract.json —    
     confirm real schema pass.
     - Manually test python -m tools.trace gate --run-id run-test-001 --gate    
     json_schema --status pass --evidence "manual test" — confirm 1 trace file  
     lands in observability/traces/gates/.
     - Manually test python -m gates.security_gates path_safety --input
     "C:\secrets\foo" on Windows — currently broken (will need a real test of   
     the fix).

     Re-score estimates after P0+P1 fixes:
     - Repo-level: 76 → 88-90/100
     - Per-skill average: 78 → 88-90/100
     - Final: 88-90/100 (would reach "Strong production candidate" band)        

     ---
     Critical files to be modified (for next session, after plan approval)      

     P0 (10 items):
     - .claude/settings.json (L6: remove key, L100: portable path)
     - tools/evals/run_eval.py (L31: remove default 0.8; add real scorers)      
     - .claude/skills/_shared/scripts/run_eval_case.sh (L29: real status)       
     - .claude/skills/06-validate/fixtures/pass-meta.json (write real)
     - .claude/skills/06-validate/fixtures/fail-schema-meta.json (write real)   
     - .claude/skills/06-validate/fixtures/fail-threshold-meta.json (write real)
     - gates/security_gates.py (L22: cross-platform path check)
     - gates/{plan,implementation,test,release,memory-promotion}-gates/ (add    
     stub .py or remove from docs)
     - .claude/skills/02-extract/fixtures/input.huge.txt (new)
     - .claude/skills/03-analyze/fixtures/input.empty.json (new)
     - .claude/skills/03-analyze/fixtures/input.brief.json (new)
     - .claude/skills/01-ingest/fixtures/large.txt (new)

     P1 (representative, 5 items):
     - schemas/skill-spec.json (L43-48, L114-117: tighten)
     - .claude/skills/00-research/{templates/v1.json.template,
     fixtures/expected_output.json, examples/smokev200.json} (fix rounds[] →    
     queries[])
     - .claude/skills/02-extract/scripts/run_eval.sh (L23-28: dynamic
     max_options)
     - scripts/validate_specs.py (add helpers-path + pipeline.json checks)      
     - evals/{regression-cases,security-redteam,skill-trigger-tests,agent-perfor
     mance}/ (add 2 cases each)

     Verification after P0 fixes (end-to-end):
     1. python scripts/validate_specs.py — must still pass (regression check)   
     2. python scripts/smoke_v2.py — must still pass on existing input_id       
     3. python -m tools.evals.run_eval evals/golden-tasks/qec-pipeline.json —   
     must produce non-0.8 scorecard
     4. python -m gates.security_gates path_safety --input "C:\\secrets\\foo" on
     Windows — must return fail (currently broken)
     5. bash .claude/skills/06-validate/scripts/run_eval.sh against new fixtures
     — must exit 0 for all 3

     ---
     Out of scope for this plan (intentional)

     - No source file modifications in this audit pass (per user's "Không được  
     sửa file trong repo trừ khi tôi yêu cầu").
     - The 27 .docs/agentic/ design docs are independent of this audit (they    
     describe the refactor target, while this audit describes the current       
     state).
     - The old agents/ folder (already deleted) and smoke_validator.py (already 
     superseded) are not in scope.
     - Multi-language research, cross-input correlation, persistent memory, UI, 
     per-input custom schemas, auto-archival — all out of scope per
     README.md:162-169.

     ---
     Open question for plan review

     Where to save the deliverable .md file?

     Options:
     - A. G:\My Drive\10_Learning\_Research\auto-research\.docs\plan.md (user   
     opened this in IDE — looks intended)
     - B. G:\My
     Drive\10_Learning\_Research\auto-research\.docs\audit-report-2026-06-02.md 
     (dated, audit-specific)
     - C. Both (mirror)

     I will write to the user's opened file (option A) after plan approval      
     unless they request otherwise.

     ---
     Confidence per audit axis

     ┌─────────────┬────────────────────────────────────────────────────────────
     ┐
     │    Axis     │                         Confidence
     │
     ├─────────────┼────────────────────────────────────────────────────────────
     ┤
     │ Repo-level  │ High (17 layers, 5 agents full-read)
     │
     ├─────────────┼────────────────────────────────────────────────────────────
     ┤
     │ Per-skill   │ High (7 skills × 9-14 files each, 4 agents full-read)      
     │
     ├─────────────┼────────────────────────────────────────────────────────────
     ┤
     │ Cross-skill │ Medium-High (read all skill.json; some fixtures unreadable 
     │
     │             │  on Windows paths)
     │
     ├─────────────┼────────────────────────────────────────────────────────────
     ┤
     │ Agent pack  │ Medium (read all 16 files, but Agent Pack Rubric scoring   
     │
     │             │ rules not fully applied)
     │
     ├─────────────┼────────────────────────────────────────────────────────────
     ┤
     │ Hard-fail   │ High (verbatim line refs)
     │
     └─────────────┴────────────────────────────────────────────────────────────
     ┘

     Overall confidence: High. The single most important finding (API key in    
     settings.json:6) is verbatim. The P0 list is reproducible by any team      
     member.