"""Rule-based checkpoints for the research pipeline.

Each gate = one Python file with a gate(input) -> GateResult function.
Run by hooks (PreToolUse) or by tools/validator.py.
"""
from __future__ import annotations

from .implementation_gates import implementation_gate
from .input_gates import completeness_gate
from .memory_promotion_gates import memory_promotion_gate
from .output_gates import evidence_grounding_gate, json_schema_gate, llm_judge_gate, manifest_consistency_gate
from .plan_gates import plan_gate
from .release_gates import release_gate
from .security_gates import path_safety_gate
from .test_gates import test_gate

__all__ = [
    "json_schema_gate",
    "llm_judge_gate",
    "manifest_consistency_gate",
    "evidence_grounding_gate",
    "completeness_gate",
    "path_safety_gate",
    "plan_gate",
    "implementation_gate",
    "test_gate",
    "release_gate",
    "memory_promotion_gate",
]
