#!/usr/bin/env python3
"""Scaffold, validate, gate, and summarise governed analytics runs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "analysis-manifest.template.json"

TOP_LEVEL_KEYS = (
    "schema_version",
    "analysis_id",
    "status",
    "needs_discovery",
    "analysis_blueprint",
    "question_tree",
    "contract",
    "sources",
    "metrics",
    "quality_checks",
    "evidence",
    "claims",
    "visuals",
    "recommendations",
    "artifacts",
    "changes",
    "approvals",
    "durable_context",
)
PROBLEM_TYPES = {
    "make_predictions",
    "categorise_things",
    "spot_unusual",
    "identify_themes",
    "discover_connections",
    "find_patterns",
}
QUESTION_ROLES = {
    "context",
    "decision",
    "diagnostic",
    "data_quality",
    "validation",
    "optional",
    "parked",
    "rejected",
    "unavailable",
    "superseded",
}
ACTIVE_QUESTION_ROLES = {"context", "decision", "diagnostic", "data_quality", "validation"}
COVERAGE_DISPOSITIONS = {
    "answered_by_question",
    "supporting_context",
    "parked",
    "rejected",
    "unavailable",
    "superseded",
}
CLAIM_STATUSES = {
    "observation",
    "candidate",
    "validated",
    "approved",
    "rejected",
    "superseded",
}
EVIDENCE_STATUSES = {"observation", "candidate", "validated", "rejected", "superseded"}
EVIDENCE_POSTURES = {"verified", "directional", "assumed", "needs_validation"}
ARTIFACT_STATUSES = {"draft", "active", "stale", "superseded", "rejected"}
LEGACY_NEEDS_MODES = {"light", "standard", "deep"}
METRIC_STATUSES = {"draft", "needs_validation", "validated", "approved", "active", "rejected", "superseded"}
CONTRACT_STATUSES = {"draft", "ready_for_review", "approved", "approved_with_caveats", "rejected"}
TREE_STATUSES = {"draft", "confirmed", "operational"}
BLUEPRINT_STATUSES = {"draft", "operational", "superseded"}
VISUAL_QA_STATUSES = {"pending", "passed", "failed", "not_possible"}
ANALYSIS_STATUSES = {
    "draft",
    "framed",
    "ready_for_execution",
    "ready_for_descriptive_results",
    "ready_for_claims",
    "ready_for_delivery",
    "blocked",
    "superseded",
}
VALIDATION_STAGES = {"contract", "evidence", "claims", "delivery"}
CLAIM_TYPES = {"descriptive", "diagnostic", "associative", "predictive", "qualitative", "causal"}
UNRESOLVED_CLAIM_TYPE = "unknown"
CLAIM_TYPE_VALUES = CLAIM_TYPES | {UNRESOLVED_CLAIM_TYPE}
TEMPORAL_SCOPES = {"full_period", "pre_outcome", "post_outcome", "cross_sectional", "not_applicable", "unknown"}
FRAMING_CONFIDENCE = {"unknown", "low", "medium", "high"}
QUALITY_STATUSES = {"pass", "warning", "fail", "unknown", "not_applicable"}
QUALITY_SEVERITIES = {"critical", "major", "minor", "info"}
QUALITY_CONDITIONS = {"always", "conditional"}
ALWAYS_QUALITY_CATEGORIES = {
    "source_authority",
    "source_freshness",
    "population_scope",
    "period_timezone",
    "grain_identifiers",
    "deduplication",
    "denominator",
    "missing_zero",
    "domain_completeness",
    "metric_semantics",
    "source_coverage",
}
CONDITIONAL_QUALITY_CATEGORIES = {
    "join_cardinality",
    "availability",
    "temporal_ordering",
    "representativeness",
    "outliers_skew",
    "minimum_sample",
    "uncertainty",
    "multiple_comparisons",
    "composition_confounding",
    "selection_bias",
    "sensitivity",
    "prediction_leakage",
    "prediction_calibration",
    "label_quality",
    "anomaly_baseline",
    "theme_validation",
    "instrumentation_semantics",
    "instrumentation_duplicates",
    "instrumentation_missing_events",
    "instrumentation_consent_coverage",
    "instrumentation_change_history",
    "instrumentation_identity",
    "experiment_eligibility",
    "experiment_randomization_unit",
    "experiment_srm",
    "experiment_sample_size",
    "experiment_peeking",
    "experiment_guardrails",
}
QUALITY_CATEGORIES = ALWAYS_QUALITY_CATEGORIES | CONDITIONAL_QUALITY_CATEGORIES
CONDITIONAL_REASONING_ROUTES = {
    "ambiguity",
    "multiple_stakeholders",
    "multiple_sources",
    "outcome_comparison",
    "sample_browser_or_qualitative_evidence",
    "prediction",
    "categorisation",
    "anomaly_detection",
    "theme_identification",
    "consequential_work",
    "instrumentation_reliability",
    "experiment",
}
ROUTE_REQUIRED_QUALITY = {
    "multiple_sources": {"join_cardinality"},
    "outcome_comparison": {"temporal_ordering", "composition_confounding", "selection_bias", "sensitivity"},
    "sample_browser_or_qualitative_evidence": {"representativeness"},
    "prediction": {"prediction_leakage", "prediction_calibration", "minimum_sample"},
    "categorisation": {"label_quality", "minimum_sample"},
    "anomaly_detection": {"anomaly_baseline"},
    "theme_identification": {"theme_validation", "representativeness"},
    "consequential_work": {"uncertainty", "sensitivity"},
    "instrumentation_reliability": {
        "instrumentation_semantics",
        "instrumentation_duplicates",
        "instrumentation_missing_events",
        "instrumentation_consent_coverage",
        "instrumentation_change_history",
    },
    "experiment": {
        "experiment_eligibility",
        "experiment_randomization_unit",
        "experiment_srm",
        "experiment_sample_size",
        "experiment_peeking",
        "experiment_guardrails",
        "uncertainty",
    },
}
ANALYSIS_BRIEF_STATUSES = {"not_started", "complete", "incomplete", "blocked"}
MEASUREMENT_CARD_FIELDS = (
    "population",
    "grain",
    "period",
    "denominator",
    "coverage",
    "unit",
    "temporal_scope",
    "missing_zero_treatment",
    "claim_posture",
    "source_ref",
)
CLAIM_CONTEXT_FIELDS = (
    "claim_type",
    "temporal_scope",
    "population",
    "denominator",
    "coverage",
    "missingness",
    "uncertainty",
    "alternative_explanations",
    "decision_use",
)
METRIC_SHAPES = {
    "count",
    "rate",
    "intensity",
    "exclusive_distribution",
    "cumulative_reach",
    "funnel",
    "trend",
    "relationship",
    "range",
    "model_metric",
    "qualitative",
}
STAKEHOLDER_VISUAL_USES = {"stakeholder", "executive", "presentation", "external"}
FINGERPRINT_FIELDS = (
    "population",
    "calculation_grain",
    "time_window",
    "scope",
    "filters",
    "numerator",
    "denominator",
    "deduplication",
    "source_query_ref",
    "run_date",
)
SOURCE_FIELDS = (
    "source_id",
    "name",
    "owner",
    "authority",
    "source_grain",
    "coverage",
    "freshness",
    "join_keys",
    "joinability",
    "allowed_uses",
    "forbidden_uses",
    "access_and_pii",
    "caveats",
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
)
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+(?:Users|Documents and Settings)[\\/]+[^\s\"'<>]+"),
    re.compile(r"(?<![A-Za-z0-9_])/(?:home|Users)/+[^\s\"'<>]+"),
    re.compile(r"(?i)(?<![A-Za-z0-9_])/(?:mnt/[a-z]/Users)/+[^\s\"'<>]+"),
    re.compile(r"(?i)(?<![A-Za-z0-9_])\\\\[^\\\s]+\\(?:Users|Documents and Settings)\\[^\s\"'<>]+"),
)
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".tsv",
    ".sql",
    ".py",
    ".js",
    ".ts",
    ".ps1",
    ".sh",
    ".toml",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "dist"}
FINGERPRINT_ALGORITHM = "sha256"


class ManifestError(ValueError):
    """Raised when a manifest cannot be loaded."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ManifestError(f"manifest does not exist: {path}") from exc
    except OSError as exc:
        raise ManifestError(f"manifest cannot be read: {path} ({exc.__class__.__name__})") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a JSON object")
    return data


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="\n") as handle:
            temp_name = handle.name
            json.dump(data, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def as_list(value: Any) -> list[Any]:
    """Return JSON arrays unchanged and treat every other value as empty."""

    return value if isinstance(value, list) else []


def string_list(item: dict[str, Any], field: str, label: str, errors: list[str]) -> list[str]:
    """Validate a list of string references without iterating strings character by character."""

    value = item.get(field, [])
    if not isinstance(value, list):
        errors.append(f"{label}.{field} must be a list")
        return []
    invalid = [index for index, entry in enumerate(value) if not isinstance(entry, str) or not entry.strip()]
    if invalid:
        errors.append(f"{label}.{field} must contain non-empty strings (invalid indexes: {invalid})")
    return [entry for entry in value if isinstance(entry, str) and entry.strip()]


def _json_output(args: argparse.Namespace) -> bool:
    return getattr(args, "format", "text") == "json"


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))


def collection_shape_errors(data: dict[str, Any], sections: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for section in sections:
        value = data.get(section, [])
        if not isinstance(value, list):
            errors.append(f"{section} must be a list")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                errors.append(f"{section}[{index}] must be an object")
    return errors


def parent_cycles(parent_map: dict[str, str]) -> list[list[str]]:
    """Find directed parent cycles in linear time."""

    finished: set[str] = set()
    cycles: list[list[str]] = []
    for start in sorted(parent_map):
        if start in finished:
            continue
        path: list[str] = []
        positions: dict[str, int] = {}
        current: str | None = start
        while current in parent_map and current not in finished and current not in positions:
            positions[current] = len(path)
            path.append(current)
            current = parent_map[current]
        if current in positions:
            cycles.append(path[positions[current]:] + [current])
        finished.update(path)
    return cycles


def require_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def keyed(items: Any, key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}[{index}] missing {key}")
            continue
        if value in result:
            errors.append(f"duplicate {key}: {value}")
        result[value] = item
    return result




def _stage_at_least(stage: str | None, minimum: str) -> bool:
    order = {"contract": 0, "evidence": 1, "claims": 2, "delivery": 3}
    return stage is not None and order[stage] >= order[minimum]


def _missing_required(item: dict[str, Any], fields: Iterable[str]) -> list[str]:
    return [field for field in fields if not require_nonempty(item.get(field))]


def _quality_gate_state(data: dict[str, Any]) -> tuple[set[str], list[str], list[str]]:
    checks = as_list(data.get("quality_checks", []))
    categories = {
        str(item.get("category"))
        for item in checks
        if isinstance(item, dict) and item.get("category") in QUALITY_CATEGORIES
    }
    blockers: list[str] = []
    warnings: list[str] = []
    for item in checks:
        if not isinstance(item, dict):
            continue
        check_id = str(item.get("check_id", "<unknown>"))
        status = item.get("status")
        severity = item.get("severity")
        if severity == "critical" and status in {"fail", "unknown"}:
            blockers.append(check_id)
        if status == "warning":
            warnings.append(check_id)
    return categories, blockers, warnings


def validate_manifest(data: dict[str, Any], strict: bool = False, stage: str | None = None) -> list[str]:
    errors: list[str] = []
    if stage is not None and stage not in VALIDATION_STAGES:
        return [f"invalid validation stage: {stage}"]
    active_stage = "delivery" if strict and stage is None else stage
    contract_required = _stage_at_least(active_stage, "contract")
    evidence_required = _stage_at_least(active_stage, "evidence")
    claims_required = _stage_at_least(active_stage, "claims")
    delivery_required = _stage_at_least(active_stage, "delivery")

    # Normalize only top-level collections in a private copy. Validation remains
    # strict, but malformed JSON values cannot crash later section checks.
    data = copy.deepcopy(data)
    for key in (
        "sources",
        "metrics",
        "quality_checks",
        "evidence",
        "claims",
        "visuals",
        "recommendations",
        "artifacts",
        "changes",
        "approvals",
        "durable_context",
    ):
        if key in data and not isinstance(data.get(key), list):
            errors.append(f"{key} must be a list")
            data[key] = []

    for key in TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    if data.get("schema_version") != "2.0":
        suffix = "; run the migrate command for a v1 manifest" if data.get("schema_version") == "1.0" else ""
        errors.append(f"schema_version must be 2.0{suffix}")
    analysis_id = data.get("analysis_id")
    if not isinstance(analysis_id, str) or not analysis_id.strip():
        errors.append("analysis_id must be a non-empty string")
    elif contract_required and analysis_id == "replace-with-analysis-id":
        errors.append("analysis_id still contains the template placeholder")
    if data.get("status") not in ANALYSIS_STATUSES:
        errors.append(f"invalid analysis status: {data.get('status')}")

    discovery = data.get("needs_discovery", {})
    if not isinstance(discovery, dict):
        errors.append("needs_discovery must be an object")
        discovery = {}
    if "mode" in discovery and discovery.get("mode") not in LEGACY_NEEDS_MODES:
        errors.append(f"invalid deprecated needs_discovery.mode: {discovery.get('mode')}")
    if discovery.get("framing_status") not in {"proposed", "confirmed", "revised", "rejected"}:
        errors.append(f"invalid needs_discovery.framing_status: {discovery.get('framing_status')}")
    if discovery.get("framing_confidence") not in FRAMING_CONFIDENCE:
        errors.append(f"invalid needs_discovery.framing_confidence: {discovery.get('framing_confidence')}")
    if not isinstance(discovery.get("user_decision_required"), bool):
        errors.append("needs_discovery.user_decision_required must be boolean")
    decomposition = discovery.get("request_decomposition", {})
    decomposition_fields = (
        "facts",
        "objectives",
        "constraints",
        "hypotheses",
        "suggested_metrics",
        "suggested_methods",
        "suggested_solutions",
        "output_preferences",
        "uncertainties",
    )
    if not isinstance(decomposition, dict):
        errors.append("needs_discovery.request_decomposition must be an object")
        decomposition = {}
    else:
        for field in decomposition_fields:
            if not isinstance(decomposition.get(field), list):
                errors.append(f"needs_discovery.request_decomposition.{field} must be a list")
    for field in ("construct_checks", "context_needs", "assumptions", "alternative_framings", "premortem_risks"):
        if not isinstance(discovery.get(field), list):
            errors.append(f"needs_discovery.{field} must be a list")
    permitted_claim_types = discovery.get("permitted_claim_types", [])
    if not isinstance(permitted_claim_types, list) or any(item not in CLAIM_TYPES for item in permitted_claim_types):
        errors.append("needs_discovery.permitted_claim_types contains an invalid claim type")

    decision = discovery.get("decision", {})
    if not isinstance(decision, dict):
        errors.append("needs_discovery.decision must be an object")
        decision = {}
    if not isinstance(decision.get("options"), list):
        errors.append("needs_discovery.decision.options must be a list")

    stated_request = discovery.get("stated_request", [])
    stated_request_ids: list[str] = []
    if not isinstance(stated_request, list):
        errors.append("needs_discovery.stated_request must be a list")
    else:
        for index, item in enumerate(stated_request):
            if not isinstance(item, dict):
                errors.append(f"needs_discovery.stated_request[{index}] must be an object")
                continue
            request_item_id = item.get("request_item_id")
            if not require_nonempty(request_item_id):
                errors.append(f"needs_discovery.stated_request[{index}] missing request_item_id")
            else:
                stated_request_ids.append(str(request_item_id))
            if not require_nonempty(item.get("text")):
                errors.append(f"needs_discovery.stated_request[{index}] missing text")
    if contract_required:
        if not stated_request_ids:
            errors.append("contract stage requires at least one stated request item")
        if not any(require_nonempty(decomposition.get(field)) for field in decomposition_fields):
            errors.append("contract stage requires a concise request decomposition")
        for field in ("inferred_business_need", "selected_framing", "framing_rationale", "evidence_ceiling"):
            if not require_nonempty(discovery.get(field)):
                errors.append(f"contract stage requires needs_discovery.{field}")
        missing_decision = _missing_required(
            decision,
            ("decision_id", "statement", "owner", "deadline_or_revisit", "consequence_of_error"),
        )
        if missing_decision:
            errors.append(f"contract stage requires a complete decision summary: {', '.join(missing_decision)}")
        if discovery.get("user_decision_required") and discovery.get("framing_status") not in {"confirmed", "revised"}:
            errors.append("material user decision remains unresolved")

    blueprint = data.get("analysis_blueprint", {})
    if not isinstance(blueprint, dict):
        errors.append("analysis_blueprint must be an object")
        blueprint = {}
    if blueprint.get("status") not in BLUEPRINT_STATUSES:
        errors.append(f"invalid analysis_blueprint.status: {blueprint.get('status')}")
    if not isinstance(blueprint.get("context_required"), bool):
        errors.append("analysis_blueprint.context_required must be boolean")
    if contract_required and not require_nonempty(blueprint.get("context_rationale")):
        errors.append("contract stage requires analysis_blueprint.context_rationale")
    routes = blueprint.get("conditional_routes", [])
    applied_routes: set[str] = set()
    if not isinstance(routes, list):
        errors.append("analysis_blueprint.conditional_routes must be a list")
    else:
        for index, route in enumerate(routes):
            if not isinstance(route, dict):
                errors.append(f"analysis_blueprint.conditional_routes[{index}] must be an object")
                continue
            for field in ("route", "trigger", "rationale"):
                if not require_nonempty(route.get(field)):
                    errors.append(f"analysis_blueprint.conditional_routes[{index}] missing {field}")
            if route.get("route") not in CONDITIONAL_REASONING_ROUTES:
                errors.append(f"analysis_blueprint.conditional_routes[{index}] has invalid route: {route.get('route')}")
            if not isinstance(route.get("applied"), bool):
                errors.append(f"analysis_blueprint.conditional_routes[{index}].applied must be boolean")
            elif route.get("applied") and route.get("route") in CONDITIONAL_REASONING_ROUTES:
                applied_routes.add(str(route["route"]))

    data_requirements = keyed(blueprint.get("data_plan", []), "data_requirement_id", "analysis_blueprint.data_plan", errors)
    allowed_requirement_types = {"context", "decision", "diagnostic", "data_quality", "validation"}
    allowed_requirement_statuses = {"draft", "unresolved", "ready", "validated", "unavailable"}
    for requirement_id, requirement in data_requirements.items():
        if requirement.get("requirement_type") not in allowed_requirement_types:
            errors.append(f"{requirement_id} has invalid requirement_type: {requirement.get('requirement_type')}")
        if requirement.get("status") not in allowed_requirement_statuses:
            errors.append(f"{requirement_id} has invalid status: {requirement.get('status')}")
        string_list(requirement, "question_ids", requirement_id, errors)
        string_list(requirement, "source_ids", requirement_id, errors)
        if contract_required:
            missing = _missing_required(
                requirement,
                ("question_ids", "purpose", "requirement_type", "population", "grain", "denominator", "measure_or_fields", "method", "validation_rules"),
            )
            if missing:
                errors.append(f"{requirement_id} incomplete data requirement: {', '.join(missing)}")
            if requirement.get("status") in {"draft", "unresolved"}:
                errors.append(f"{requirement_id} is unresolved at contract stage")
    if contract_required:
        if blueprint.get("status") != "operational":
            errors.append("contract stage requires an operational analysis blueprint")
        if not require_nonempty(blueprint.get("stop_rule")):
            errors.append("contract stage requires analysis_blueprint.stop_rule")
        if not data_requirements:
            errors.append("contract stage requires a non-empty analysis data plan")

    tree = data.get("question_tree", {})
    if not isinstance(tree, dict):
        errors.append("question_tree must be an object")
        tree = {}
    if tree.get("status") not in TREE_STATUSES:
        errors.append(f"invalid question_tree.status: {tree.get('status')}")
    primary_type = tree.get("primary_problem_type")
    if primary_type not in PROBLEM_TYPES:
        errors.append(f"invalid primary problem type: {primary_type}")
    secondary = tree.get("secondary_problem_types", [])
    if not isinstance(secondary, list) or any(item not in PROBLEM_TYPES for item in secondary):
        errors.append("secondary_problem_types contains an invalid type")
        secondary = []
    if primary_type in secondary:
        errors.append("primary problem type must not be repeated as secondary")
    declared_problem_types = ({primary_type} if primary_type in PROBLEM_TYPES else set()) | {
        item for item in secondary if item in PROBLEM_TYPES
    }

    questions = keyed(tree.get("questions", []), "question_id", "question_tree.questions", errors)
    for question_id, question in questions.items():
        role = question.get("role")
        if role not in QUESTION_ROLES:
            errors.append(f"{question_id} has invalid role: {role}")
        if role in ACTIVE_QUESTION_ROLES and question.get("problem_type") not in PROBLEM_TYPES:
            errors.append(f"{question_id} has invalid problem_type: {question.get('problem_type')}")
        elif role in ACTIVE_QUESTION_ROLES and question.get("problem_type") not in declared_problem_types:
            errors.append(f"{question_id} uses an undeclared problem_type: {question.get('problem_type')}")
        parent = question.get("parent_id")
        if parent is not None and parent not in questions:
            errors.append(f"{question_id} references missing parent question: {parent}")
        if parent == question_id:
            errors.append(f"{question_id} cannot be its own parent")
        requirement_ids = string_list(question, "data_requirement_ids", question_id, errors)
        string_list(question, "source_ids", question_id, errors)
        string_list(question, "metric_ids", question_id, errors)
        for requirement_id in requirement_ids:
            if requirement_id not in data_requirements:
                errors.append(f"{question_id} references missing data requirement: {requirement_id}")
        if contract_required and role in ACTIVE_QUESTION_ROLES:
            missing = _missing_required(
                question,
                ("text", "purpose", "decision_relevance", "data_requirement_ids", "population", "grain", "method", "validation_rules", "expected_output"),
            )
            if missing:
                errors.append(f"{question_id} incomplete operational question: {', '.join(missing)}")
            if question.get("status") not in {"operational", "answered"}:
                errors.append(f"{question_id} is not operational at contract stage")
    parent_map = {
        question_id: question.get("parent_id")
        for question_id, question in questions.items()
        if isinstance(question.get("parent_id"), str) and question.get("parent_id") in questions
    }
    for cycle in parent_cycles(parent_map):
        errors.append(f"question tree contains a parent cycle: {' -> '.join(cycle)}")
    for requirement_id, requirement in data_requirements.items():
        for question_id in as_list(requirement.get("question_ids", [])):
            if question_id not in questions:
                errors.append(f"{requirement_id} references missing question: {question_id}")
            elif requirement_id not in as_list(questions[question_id].get("data_requirement_ids", [])):
                errors.append(f"{requirement_id} is not linked back from {question_id}")
    if contract_required:
        if tree.get("status") != "operational":
            errors.append("contract stage requires an operational question tree")
        if not any(question.get("role") == "decision" for question in questions.values()):
            errors.append("contract stage requires at least one decision question")
        active_context = [question_id for question_id, question in questions.items() if question.get("role") == "context"]
        if blueprint.get("context_required") and not active_context:
            errors.append("analysis blueprint requires context but has no active context question")
        if not blueprint.get("context_required") and active_context:
            errors.append(f"active context questions require context_required=true: {active_context}")
        if "consequential_work" in applied_routes and not discovery.get("premortem_risks"):
            errors.append("consequential work requires at least one pre-mortem risk")

    coverage = tree.get("coverage", [])
    coverage_ids: list[str] = []
    if not isinstance(coverage, list):
        errors.append("question_tree.coverage must be a list")
    else:
        for index, item in enumerate(coverage):
            if not isinstance(item, dict):
                errors.append(f"question_tree.coverage[{index}] must be an object")
                continue
            request_item_id = item.get("request_item_id")
            if not require_nonempty(request_item_id):
                errors.append(f"question_tree.coverage[{index}] missing request_item_id")
            else:
                coverage_ids.append(str(request_item_id))
            disposition = item.get("disposition")
            if disposition not in COVERAGE_DISPOSITIONS:
                errors.append(f"question_tree.coverage[{index}] has invalid disposition: {disposition}")
            question_refs = string_list(item, "question_ids", f"question_tree.coverage[{index}]", errors)
            for question_id in question_refs:
                if question_id not in questions:
                    errors.append(f"question_tree.coverage[{index}] references missing question: {question_id}")
            if disposition not in {"answered_by_question", "supporting_context"} and not require_nonempty(item.get("reason")):
                errors.append(f"question_tree.coverage[{index}] requires a reason for disposition {disposition}")
        for repeated, count in sorted(Counter(coverage_ids).items()):
            if count <= 1:
                continue
            errors.append(f"duplicate request coverage item: {repeated}")
    if contract_required and stated_request_ids:
        missing_coverage = sorted(set(stated_request_ids) - set(coverage_ids))
        if missing_coverage:
            errors.append(f"request coverage missing stated items: {missing_coverage}")

    contract = data.get("contract", {})
    if not isinstance(contract, dict):
        errors.append("contract must be an object")
        contract = {}
    if contract.get("status") not in CONTRACT_STATUSES:
        errors.append(f"invalid contract.status: {contract.get('status')}")
    if contract.get("risk") not in {"low", "medium", "high"}:
        errors.append(f"invalid contract.risk: {contract.get('risk')}")
    if contract_required:
        if contract.get("status") not in {"approved", "approved_with_caveats"}:
            errors.append("contract stage requires an approved contract")
        missing = _missing_required(contract, ("audience", "owner", "population", "primary_grain", "definition_of_done"))
        if missing:
            errors.append(f"approved contract missing fields: {', '.join(missing)}")
        period = contract.get("period", {})
        if not isinstance(period, dict) or any(not require_nonempty(period.get(field)) for field in ("start", "end", "timezone")):
            errors.append("approved contract requires period start, end, and timezone")
        if contract.get("risk") in {"medium", "high"} and not require_nonempty(contract.get("approval_gates")):
            errors.append("medium/high-risk approved contract requires approval_gates")

    sources = keyed(data.get("sources", []), "source_id", "sources", errors)
    for source_id, source in sources.items():
        missing = [field for field in SOURCE_FIELDS if field not in source]
        if missing:
            errors.append(f"{source_id} missing source fields: {', '.join(missing)}")
        if source.get("authority") not in {"canonical", "supporting", "illustrative", "experimental"}:
            errors.append(f"{source_id} has invalid authority: {source.get('authority')}")
        if source.get("joinability") not in {"direct", "aggregate_only", "none", "unknown"}:
            errors.append(f"{source_id} has invalid joinability: {source.get('joinability')}")
        if evidence_required:
            missing_source_context = _missing_required(
                source,
                ("name", "owner", "source_grain", "coverage", "freshness", "allowed_uses", "access_and_pii"),
            )
            if missing_source_context:
                errors.append(f"{source_id} incomplete source context: {', '.join(missing_source_context)}")
            freshness = source.get("freshness", {})
            if not isinstance(freshness, dict) or any(
                not require_nonempty(freshness.get(field)) for field in ("valid_as_of", "revalidate_after")
            ):
                errors.append(f"{source_id} freshness requires valid_as_of and revalidate_after")
            if source.get("joinability") == "direct" and not require_nonempty(source.get("join_keys")):
                errors.append(f"{source_id} direct joinability requires join_keys")
    if evidence_required and not sources:
        errors.append("evidence stage requires at least one source")
    for requirement_id, requirement in data_requirements.items():
        for source_id in as_list(requirement.get("source_ids", [])):
            if source_id not in sources:
                errors.append(f"{requirement_id} references missing source: {source_id}")

    metrics = keyed(data.get("metrics", []), "metric_id", "metrics", errors)
    metric_hashes: dict[str, str] = {}
    metric_contract_fields = (
        "construct",
        "measurement_limit",
        "coverage",
        "missingness",
        "estimand",
        "baseline",
        "time_logic",
        "uncertainty_method",
        "sensitivity_checks",
        "permitted_claim_types",
    )
    for metric_id, metric in metrics.items():
        metric_question_ids = string_list(metric, "question_ids", metric_id, errors)
        metric_source_ids = string_list(metric, "source_ids", metric_id, errors)
        for question_id in metric_question_ids:
            if question_id not in questions:
                errors.append(f"{metric_id} references missing question: {question_id}")
        for source_id in metric_source_ids:
            if source_id not in sources:
                errors.append(f"{metric_id} references missing source: {source_id}")
        if metric.get("status") not in METRIC_STATUSES:
            errors.append(f"{metric_id} has invalid status: {metric.get('status')}")
        if metric.get("metric_shape") not in METRIC_SHAPES:
            errors.append(f"{metric_id} has invalid metric_shape: {metric.get('metric_shape')}")
        permitted = metric.get("permitted_claim_types", [])
        if permitted and (not isinstance(permitted, list) or any(item not in CLAIM_TYPES for item in permitted)):
            errors.append(f"{metric_id} has invalid permitted_claim_types")
        fingerprint = metric.get("definition_fingerprint")
        if not isinstance(fingerprint, dict):
            errors.append(f"{metric_id} missing definition_fingerprint")
            continue
        if evidence_required or metric.get("status") in {"validated", "approved", "active"}:
            missing_keys = [field for field in FINGERPRINT_FIELDS if field not in fingerprint]
            if missing_keys:
                errors.append(f"{metric_id} fingerprint missing fields: {', '.join(missing_keys)}")
            missing_values = [
                field
                for field in FINGERPRINT_FIELDS
                if field not in {"scope", "filters"} and not require_nonempty(fingerprint.get(field))
            ]
            if missing_values:
                errors.append(f"{metric_id} incomplete fingerprint: {', '.join(missing_values)}")
            if "scope" in fingerprint and not isinstance(fingerprint.get("scope"), dict):
                errors.append(f"{metric_id} fingerprint.scope must be an object")
            if "filters" in fingerprint and not isinstance(fingerprint.get("filters"), list):
                errors.append(f"{metric_id} fingerprint.filters must be a list")
            time_window = fingerprint.get("time_window", {})
            if not isinstance(time_window, dict) or any(not require_nonempty(time_window.get(field)) for field in ("start", "end", "timezone")):
                errors.append(f"{metric_id} fingerprint requires start, end, and timezone")
            missing_contract = _missing_required(metric, metric_contract_fields)
            if missing_contract:
                errors.append(f"{metric_id} incomplete method contract: {', '.join(missing_contract)}")
            missing_links = _missing_required(metric, ("question_ids", "source_ids"))
            if missing_links:
                errors.append(f"{metric_id} incomplete lineage: {', '.join(missing_links)}")
        expected = metric.get("expected_domain")
        observed = metric.get("observed_domain")
        if expected is not None:
            if not isinstance(expected, list) or not isinstance(observed, list):
                errors.append(f"{metric_id} expected_domain and observed_domain must both be lists")
            else:
                missing_values = [value for value in expected if value not in observed]
                if missing_values:
                    errors.append(f"{metric_id} observed_domain missing expected values: {missing_values}")
        metric_hashes[metric_id] = stable_hash(fingerprint)
        if (evidence_required or metric.get("status") in {"validated", "approved", "active"}) and not require_nonempty(
            metric.get("fingerprint_hash")
        ):
            errors.append(f"{metric_id} requires fingerprint_hash")
        elif metric.get("fingerprint_hash") and metric.get("fingerprint_hash") != metric_hashes[metric_id]:
            errors.append(f"{metric_id} fingerprint_hash is stale")
    if evidence_required and not metrics:
        errors.append("evidence stage requires at least one metric")
    for question_id, question in questions.items():
        for source_id in as_list(question.get("source_ids", [])):
            if source_id not in sources:
                errors.append(f"{question_id} references missing source: {source_id}")
        for metric_id in as_list(question.get("metric_ids", [])):
            if metric_id not in metrics:
                errors.append(f"{question_id} references missing metric: {metric_id}")

    quality_checks = keyed(data.get("quality_checks", []), "check_id", "quality_checks", errors)
    for check_id, check in quality_checks.items():
        category = check.get("category")
        if category not in QUALITY_CATEGORIES:
            errors.append(f"{check_id} has invalid quality category: {category}")
        if check.get("condition") not in QUALITY_CONDITIONS:
            errors.append(f"{check_id} has invalid quality condition: {check.get('condition')}")
        status = check.get("status")
        if status not in QUALITY_STATUSES:
            errors.append(f"{check_id} has invalid quality status: {status}")
        if check.get("severity") not in QUALITY_SEVERITIES:
            errors.append(f"{check_id} has invalid quality severity: {check.get('severity')}")
        check_question_ids = string_list(check, "question_ids", check_id, errors)
        check_source_ids = string_list(check, "source_ids", check_id, errors)
        check_metric_ids = string_list(check, "metric_ids", check_id, errors)
        for question_id in check_question_ids:
            if question_id not in questions:
                errors.append(f"{check_id} references missing question: {question_id}")
        for source_id in check_source_ids:
            if source_id not in sources:
                errors.append(f"{check_id} references missing source: {source_id}")
        for metric_id in check_metric_ids:
            if metric_id not in metrics:
                errors.append(f"{check_id} references missing metric: {metric_id}")
        if evidence_required and status in {"pass", "warning", "fail"} and not require_nonempty(check.get("evidence_ref")):
            errors.append(f"{check_id} status {status} requires evidence_ref")
        if evidence_required and status in {"pass", "warning", "fail", "not_applicable"} and not require_nonempty(check.get("checked_at")):
            errors.append(f"{check_id} status {status} requires checked_at")
        if status in {"warning", "fail", "unknown"}:
            missing = _missing_required(check, ("impact", "required_action"))
            if missing:
                errors.append(f"{check_id} incomplete quality exception: {', '.join(missing)}")
        if status == "not_applicable" and not (require_nonempty(check.get("impact")) or require_nonempty(check.get("required_action"))):
            errors.append(f"{check_id} not_applicable requires a rationale")
    quality_categories, quality_blockers, quality_warnings = _quality_gate_state(data)
    if evidence_required:
        missing_categories = sorted(ALWAYS_QUALITY_CATEGORIES - quality_categories)
        if missing_categories:
            errors.append(f"evidence stage missing always-on quality categories: {missing_categories}")
        for route in sorted(applied_routes):
            missing_route_checks = sorted(ROUTE_REQUIRED_QUALITY.get(route, set()) - quality_categories)
            if missing_route_checks:
                errors.append(f"route {route} missing conditional quality categories: {missing_route_checks}")
    if claims_required and quality_blockers:
        errors.append(f"claim promotion blocked by critical quality checks: {quality_blockers}")

    evidence = keyed(data.get("evidence", []), "evidence_id", "evidence", errors)
    for evidence_id, evidence_item in evidence.items():
        status = evidence_item.get("status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{evidence_id} has invalid status: {status}")
        evidence_question_ids = string_list(evidence_item, "question_ids", evidence_id, errors)
        evidence_source_ids = string_list(evidence_item, "source_ids", evidence_id, errors)
        for question_id in evidence_question_ids:
            if question_id not in questions:
                errors.append(f"{evidence_id} references missing question: {question_id}")
        for source_id in evidence_source_ids:
            if source_id not in sources:
                errors.append(f"{evidence_id} references missing source: {source_id}")
        if status == "validated":
            missing_evidence_context = _missing_required(evidence_item, ("question_ids", "source_ids", "result_ref"))
            if missing_evidence_context:
                errors.append(f"{evidence_id} incomplete validated evidence: {', '.join(missing_evidence_context)}")

    claims = keyed(data.get("claims", []), "claim_id", "claims", errors)
    for claim_id, claim in claims.items():
        status = claim.get("status")
        if status not in CLAIM_STATUSES:
            errors.append(f"{claim_id} has invalid status: {status}")
        posture = claim.get("evidence_posture")
        if posture not in EVIDENCE_POSTURES:
            errors.append(f"{claim_id} has invalid evidence_posture: {posture}")
        if claim.get("claim_type") not in CLAIM_TYPE_VALUES:
            errors.append(f"{claim_id} has invalid claim_type: {claim.get('claim_type')}")
        if claim.get("temporal_scope") not in TEMPORAL_SCOPES:
            errors.append(f"{claim_id} has invalid temporal_scope: {claim.get('temporal_scope')}")
        claim_question_ids = string_list(claim, "question_ids", claim_id, errors)
        claim_metric_ids = string_list(claim, "metric_ids", claim_id, errors)
        claim_evidence_refs = string_list(claim, "evidence_refs", claim_id, errors)
        claim_quality_refs = string_list(claim, "quality_check_refs", claim_id, errors)
        for question_id in claim_question_ids:
            if question_id not in questions:
                errors.append(f"{claim_id} references missing question: {question_id}")
        for metric_id in claim_metric_ids:
            if metric_id not in metrics:
                errors.append(f"{claim_id} references missing metric: {metric_id}")
            elif metrics[metric_id].get("permitted_claim_types") and claim.get("claim_type") not in metrics[metric_id].get("permitted_claim_types", []):
                errors.append(f"{claim_id} claim_type is not permitted by {metric_id}")
        for evidence_id in claim_evidence_refs:
            if evidence_id not in evidence:
                errors.append(f"{claim_id} references missing evidence: {evidence_id}")
        for check_id in claim_quality_refs:
            if check_id not in quality_checks:
                errors.append(f"{claim_id} references missing quality check: {check_id}")
        snapshots = claim.get("metric_fingerprints", {})
        if not isinstance(snapshots, dict):
            errors.append(f"{claim_id} metric_fingerprints must be an object")
            snapshots = {}
        for metric_id, snapshot in snapshots.items():
            if metric_id not in metric_hashes:
                errors.append(f"{claim_id} snapshots missing metric: {metric_id}")
            elif snapshot != metric_hashes[metric_id] and status not in {"candidate", "rejected", "superseded"}:
                errors.append(f"{claim_id} has stale metric fingerprint for {metric_id}")
        comparison_ids = string_list(claim, "comparison_metric_ids", claim_id, errors) if "comparison_metric_ids" in claim else []
        if comparison_ids:
            missing_metrics = [metric_id for metric_id in comparison_ids if metric_id not in metrics]
            if missing_metrics:
                errors.append(f"{claim_id} comparison references missing metrics: {missing_metrics}")
            elif len(comparison_ids) >= 2:
                compatibility_keys = claim.get(
                    "compatibility_keys",
                    ["population", "calculation_grain", "time_window", "scope", "denominator", "deduplication"],
                )
                if not isinstance(compatibility_keys, list) or any(not isinstance(key, str) for key in compatibility_keys):
                    errors.append(f"{claim_id}.compatibility_keys must be a list of strings")
                    compatibility_keys = []
                baseline = metrics[comparison_ids[0]].get("definition_fingerprint", {})
                mismatches = [
                    key
                    for key in compatibility_keys
                    if any(metrics[metric_id].get("definition_fingerprint", {}).get(key) != baseline.get(key) for metric_id in comparison_ids[1:])
                ]
                if mismatches and not require_nonempty(claim.get("compatibility_rationale")):
                    errors.append(f"{claim_id} compares incompatible fingerprints without rationale: {mismatches}")
        if not isinstance(claim.get("alternative_explanations"), list):
            errors.append(f"{claim_id}.alternative_explanations must be a list")
        if status in {"validated", "approved"}:
            if claim.get("claim_type") == UNRESOLVED_CLAIM_TYPE:
                errors.append(f"{claim_id} cannot be {status} with an unresolved claim_type")
            context_fields = tuple(field for field in CLAIM_CONTEXT_FIELDS if field != "alternative_explanations")
            missing_context = _missing_required(claim, ("statement", "question_ids", *context_fields))
            if missing_context:
                errors.append(f"{claim_id} incomplete claim context: {', '.join(missing_context)}")
            if claim.get("claim_type") not in permitted_claim_types:
                errors.append(f"{claim_id} exceeds the needs-discovery evidence ceiling")
            if not claim.get("evidence_refs"):
                errors.append(f"{claim_id} cannot be {status} without evidence_refs")
            if not claim.get("metric_ids") and posture != "directional":
                errors.append(f"{claim_id} cannot be {status} without metric_ids unless directional")
            if not require_nonempty(claim.get("valid_as_of")):
                errors.append(f"{claim_id} cannot be {status} without valid_as_of")
            missing_snapshots = [metric_id for metric_id in claim_metric_ids if metric_id not in snapshots]
            if missing_snapshots:
                errors.append(f"{claim_id} missing metric fingerprint snapshots: {missing_snapshots}")
            unvalidated = [evidence_id for evidence_id in claim_evidence_refs if evidence.get(evidence_id, {}).get("status") != "validated"]
            if unvalidated:
                errors.append(f"{claim_id} uses evidence that is not validated: {unvalidated}")
            claim_source_ids = {
                source_id
                for metric_id in claim_metric_ids
                for source_id in as_list(metrics.get(metric_id, {}).get("source_ids", []))
            } | {
                source_id
                for evidence_id in claim_evidence_refs
                for source_id in as_list(evidence.get(evidence_id, {}).get("source_ids", []))
            }
            relevant_warnings = {
                check_id
                for check_id, check in quality_checks.items()
                if check.get("status") == "warning"
                and (
                    set(as_list(check.get("question_ids", []))) & set(claim_question_ids)
                    or set(as_list(check.get("metric_ids", []))) & set(claim_metric_ids)
                    or set(as_list(check.get("source_ids", []))) & claim_source_ids
                )
            }
            missing_warnings = sorted(relevant_warnings - set(claim_quality_refs))
            if missing_warnings:
                errors.append(f"{claim_id} does not reference relevant quality warnings: {missing_warnings}")
        if claim.get("claim_type") == "causal" and status in {"validated", "approved"} and not require_nonempty(claim.get("causal_design_ref")):
            errors.append(f"{claim_id} causal claim requires causal_design_ref")
        if status == "approved" and (not require_nonempty(claim.get("approved_by")) or not require_nonempty(claim.get("approved_at"))):
            errors.append(f"{claim_id} cannot be approved without approved_by and approved_at")

    visuals = keyed(data.get("visuals", []), "visual_id", "visuals", errors)
    for visual_id, visual in visuals.items():
        claim_ids = string_list(visual, "claim_ids", visual_id, errors)
        for claim_id in claim_ids:
            if claim_id not in claims:
                errors.append(f"{visual_id} references missing claim: {claim_id}")
        intended_use = visual.get("intended_use", "stakeholder")
        if claims_required and intended_use in STAKEHOLDER_VISUAL_USES:
            if not require_nonempty(claim_ids):
                errors.append(f"{visual_id} stakeholder visual requires claim_ids")
            for claim_id in claim_ids:
                if claims.get(claim_id, {}).get("status") != "approved":
                    errors.append(f"{visual_id} stakeholder visual uses non-approved claim: {claim_id}")
        qa_status = visual.get("qa_status")
        if qa_status not in VISUAL_QA_STATUSES:
            errors.append(f"{visual_id} has invalid qa_status: {qa_status}")
        structure = visual.get("data_structure", {}) if isinstance(visual.get("data_structure"), dict) else {}
        shape = structure.get("metric_shape")
        selected = str(visual.get("selected_chart", "")).lower()
        chart_tokens = set(re.findall(r"[a-z0-9]+", selected))
        if shape == "exclusive_distribution" and "funnel" in chart_tokens:
            errors.append(f"{visual_id} cannot use a funnel for an exclusive distribution")
        if structure.get("ordered") is False and "line" in chart_tokens:
            errors.append(f"{visual_id} cannot use a line for unordered categories")
        if structure.get("categories_overlap") is True and visual.get("communication_function") in {"proportion", "part_to_whole"}:
            errors.append(f"{visual_id} cannot use part-to-whole encoding for overlapping categories")
        visual_quality_refs = string_list(visual, "quality_check_refs", visual_id, errors)
        for check_id in visual_quality_refs:
            if check_id not in quality_checks:
                errors.append(f"{visual_id} references missing quality check: {check_id}")
        if delivery_required and intended_use in STAKEHOLDER_VISUAL_USES:
            missing = _missing_required(visual, ("question_id", "result_ref", "message", "communication_function", "selected_chart", "selection_rationale", "required_labels"))
            if missing:
                errors.append(f"{visual_id} incomplete stakeholder visual: {', '.join(missing)}")
            if qa_status != "passed":
                errors.append(f"{visual_id} stakeholder visual has not passed rendered QA")
            if not isinstance(visual.get("live_catalogue_checked"), bool):
                errors.append(f"{visual_id} must record whether the live catalogue was checked")
            elif visual.get("live_catalogue_checked") is False and not require_nonempty(visual.get("catalogue_check_note")):
                errors.append(f"{visual_id} must explain why the live catalogue was not checked")
            card = visual.get("measurement_card", {})
            if not isinstance(card, dict):
                errors.append(f"{visual_id} measurement_card must be an object")
            else:
                missing_card = _missing_required(card, MEASUREMENT_CARD_FIELDS)
                if missing_card:
                    errors.append(f"{visual_id} incomplete measurement card: {', '.join(missing_card)}")
            wording = visual.get("wording_review", {})
            if not isinstance(wording, dict):
                errors.append(f"{visual_id} wording_review must be an object")
            else:
                for field in ("audience", "language", "terminology_source", "notes"):
                    if not require_nonempty(wording.get(field)):
                        errors.append(f"{visual_id} wording_review missing {field}")
                if wording.get("plain_language_passed") is not True:
                    errors.append(f"{visual_id} has not passed plain-language review")
                if wording.get("fact_interpretation_recommendation_separated") is not True:
                    errors.append(f"{visual_id} has not separated fact, interpretation, and recommendation")
            inherited_warnings = {
                check_id
                for claim_id in claim_ids
                for check_id in as_list(claims.get(claim_id, {}).get("quality_check_refs", []))
                if quality_checks.get(check_id, {}).get("status") == "warning"
            }
            missing_visual_warnings = sorted(inherited_warnings - set(visual_quality_refs))
            if missing_visual_warnings:
                errors.append(f"{visual_id} does not carry claim quality warnings: {missing_visual_warnings}")

    recommendations = keyed(data.get("recommendations", []), "recommendation_id", "recommendations", errors)
    recommendation_fields = (
        "decision_id",
        "supporting_claim_ids",
        "hypothesis",
        "expected_mechanism",
        "target_population",
        "action",
        "success_metrics",
        "guardrails",
        "implementation_requirement",
        "owner",
        "revisit_condition",
    )
    for recommendation_id, recommendation in recommendations.items():
        supporting = string_list(recommendation, "supporting_claim_ids", recommendation_id, errors)
        if claims_required and not supporting:
            errors.append(f"{recommendation_id} has no supporting_claim_ids")
        for claim_id in supporting:
            if claim_id not in claims:
                errors.append(f"{recommendation_id} references missing claim: {claim_id}")
            elif claims_required and claims[claim_id].get("status") != "approved":
                errors.append(f"{recommendation_id} uses non-approved claim: {claim_id}")
        if claims_required:
            missing = _missing_required(recommendation, recommendation_fields)
            if missing:
                errors.append(f"{recommendation_id} incomplete recommendation: {', '.join(missing)}")

    brief = data.get("analysis_brief")
    brief_claim_ids: list[str] = []
    if brief is not None:
        if not isinstance(brief, dict):
            errors.append("analysis_brief must be an object")
            brief = {}
        if brief.get("answer_status") not in ANALYSIS_BRIEF_STATUSES:
            errors.append(f"invalid analysis_brief.answer_status: {brief.get('answer_status')}")
        brief_claim_ids = string_list(brief, "key_claim_ids", "analysis_brief", errors)
        for field in ("alternative_explanations", "limitations", "unknowns", "methods_refs"):
            string_list(brief, field, "analysis_brief", errors)
        for claim_id in brief_claim_ids:
            if claim_id not in claims:
                errors.append(f"analysis_brief references missing claim: {claim_id}")
            elif brief.get("answer_status") != "not_started" and claims[claim_id].get("status") != "approved":
                errors.append(f"analysis_brief uses non-approved claim: {claim_id}")
        if brief.get("answer_status") == "complete" and not brief_claim_ids:
            errors.append("complete analysis_brief requires key_claim_ids")
        if brief.get("answer_status") in {"incomplete", "blocked"} and not require_nonempty(brief.get("unknowns")):
            errors.append(f"{brief.get('answer_status')} analysis_brief requires explicit unknowns")
        if delivery_required:
            if brief.get("answer_status") == "not_started":
                errors.append("delivery stage requires a completed, incomplete, or blocked analysis brief")
            missing_brief = _missing_required(
                brief,
                ("business_question", "executive_answer", "interpretation", "recommended_next_action"),
            )
            if missing_brief:
                errors.append(f"delivery stage requires a decision-ready analysis brief: {', '.join(missing_brief)}")

    if delivery_required:
        brief_is_decision_ready = (
            isinstance(brief, dict)
            and brief.get("answer_status") in {"complete", "incomplete", "blocked"}
            and not _missing_required(
                brief,
                ("business_question", "executive_answer", "interpretation", "recommended_next_action"),
            )
            and (brief.get("answer_status") != "complete" or bool(brief_claim_ids))
            and (brief.get("answer_status") not in {"incomplete", "blocked"} or require_nonempty(brief.get("unknowns")))
        )
        has_passed_stakeholder_visual = any(
            visual.get("intended_use", "stakeholder") in STAKEHOLDER_VISUAL_USES
            and visual.get("qa_status") == "passed"
            for visual in visuals.values()
        )
        if not brief_is_decision_ready and not has_passed_stakeholder_visual:
            errors.append("delivery stage requires a decision-ready analysis brief or a stakeholder visual with passed rendered QA")

    artifacts = keyed(data.get("artifacts", []), "artifact_id", "artifacts", errors)
    known_dependencies = set(questions) | set(sources) | set(metrics) | set(quality_checks) | set(evidence) | set(claims) | set(visuals) | set(recommendations)
    for artifact_id, artifact in artifacts.items():
        if artifact.get("status") not in ARTIFACT_STATUSES:
            errors.append(f"{artifact_id} has invalid status: {artifact.get('status')}")
        if delivery_required and artifact.get("status") == "active":
            missing_artifact_context = _missing_required(artifact, ("purpose", "path", "depends_on"))
            if missing_artifact_context:
                errors.append(f"{artifact_id} incomplete active artifact: {', '.join(missing_artifact_context)}")
        dependencies = string_list(artifact, "depends_on", artifact_id, errors)
        for dependency in dependencies:
            if dependency not in known_dependencies:
                errors.append(f"{artifact_id} references missing dependency: {dependency}")
        snapshots = artifact.get("metric_fingerprints", {})
        if not isinstance(snapshots, dict):
            errors.append(f"{artifact_id} metric_fingerprints must be an object")
            snapshots = {}
        for metric_id, snapshot in snapshots.items():
            if metric_id not in metric_hashes:
                errors.append(f"{artifact_id} snapshots missing metric: {metric_id}")
            elif snapshot != metric_hashes[metric_id] and artifact.get("status") not in {"stale", "superseded"}:
                errors.append(f"{artifact_id} has stale metric fingerprint for {metric_id}")
        required_snapshots = {dependency for dependency in dependencies if dependency in metrics}
        for dependency in dependencies:
            if dependency in claims:
                required_snapshots.update(as_list(claims[dependency].get("metric_ids", [])))
        if artifact.get("status") == "active":
            missing_snapshots = sorted(required_snapshots - set(snapshots))
            if missing_snapshots:
                errors.append(f"{artifact_id} missing metric fingerprint snapshots: {missing_snapshots}")

    active_purposes: dict[str, list[str]] = {}
    for artifact_id, artifact in artifacts.items():
        if artifact.get("status") == "active" and require_nonempty(artifact.get("purpose")):
            active_purposes.setdefault(str(artifact["purpose"]), []).append(artifact_id)
    for purpose, artifact_ids in active_purposes.items():
        if len(artifact_ids) > 1:
            errors.append(f"multiple active artifacts for purpose {purpose!r}: {artifact_ids}")

    allowed_statuses_by_stage = {
        "contract": {"framed", "ready_for_execution", "ready_for_descriptive_results", "ready_for_claims", "ready_for_delivery"},
        "evidence": {"ready_for_execution", "ready_for_descriptive_results", "ready_for_claims", "ready_for_delivery", "blocked"},
        "claims": {"ready_for_claims", "ready_for_delivery"},
        "delivery": {"ready_for_delivery"},
    }
    if active_stage and data.get("status") not in allowed_statuses_by_stage[active_stage]:
        errors.append(f"analysis status {data.get('status')} is not ready for {active_stage} validation")
    if claims_required and not any(claim.get("status") in {"validated", "approved"} for claim in claims.values()):
        errors.append("claims stage requires at least one validated or approved claim")
    if delivery_required and not any(artifact.get("status") == "active" for artifact in artifacts.values()):
        errors.append("delivery stage requires at least one active artifact")

    return errors


def migrate_v1_manifest(data: dict[str, Any]) -> dict[str, Any]:
    version = data.get("schema_version")
    if version == "2.0":
        return copy.deepcopy(data)
    if version != "1.0":
        raise ManifestError(f"cannot migrate schema_version {version!r}; expected 1.0")

    migrated = copy.deepcopy(data)
    migrated["schema_version"] = "2.0"
    migrated["status"] = "draft"
    discovery = migrated.get("needs_discovery")
    if not isinstance(discovery, dict):
        discovery = {}
        migrated["needs_discovery"] = discovery
    legacy_mode = discovery.pop("mode", None)
    discovery.setdefault(
        "request_decomposition",
        {
            "facts": [],
            "objectives": [],
            "constraints": [],
            "hypotheses": [],
            "suggested_metrics": [],
            "suggested_methods": [],
            "suggested_solutions": [],
            "output_preferences": [],
            "uncertainties": [],
        },
    )
    discovery.setdefault("selected_framing", discovery.get("inferred_business_need", ""))
    discovery.setdefault("framing_rationale", "")
    discovery.setdefault("framing_confidence", "unknown")
    discovery.setdefault("construct_checks", [])
    discovery.setdefault("context_needs", [])
    discovery.setdefault("permitted_claim_types", [])
    discovery.setdefault("user_decision_required", legacy_mode in {"standard", "deep"})
    discovery["framing_status"] = "proposed"

    role_map = {
        "core": "decision",
        "supporting": "context",
        "diagnostic": "diagnostic",
        "optional": "optional",
        "duplicate": "rejected",
        "misleading": "rejected",
        "unavailable": "unavailable",
        "out_of_scope": "rejected",
    }
    tree = migrated.get("question_tree")
    if not isinstance(tree, dict):
        tree = {}
        migrated["question_tree"] = tree
    tree["status"] = "draft"
    contract = migrated.get("contract")
    if not isinstance(contract, dict):
        contract = {}
        migrated["contract"] = contract
    if contract.get("status") in {"approved", "approved_with_caveats"}:
        contract["legacy_status"] = contract["status"]
        contract["status"] = "ready_for_review"

    data_plan: list[dict[str, Any]] = []
    for question in as_list(tree.get("questions", [])):
        if not isinstance(question, dict):
            continue
        legacy_role = question.get("role")
        question["legacy_role"] = legacy_role
        question["role"] = role_map.get(str(legacy_role), "rejected")
        question.setdefault("purpose", question.get("decision_relevance", ""))
        question.setdefault("population", contract.get("population", ""))
        question.setdefault("grain", contract.get("primary_grain", ""))
        question.setdefault("data_requirement_ids", [])
        if question.get("role") in ACTIVE_QUESTION_ROLES:
            requirement_id = f"DR-{question.get('question_id', 'UNKNOWN')}"
            question["data_requirement_ids"] = [requirement_id]
            question["legacy_status"] = question.get("status")
            question["status"] = "draft"
            data_plan.append(
                {
                    "data_requirement_id": requirement_id,
                    "question_ids": [question.get("question_id")],
                    "purpose": question.get("purpose", ""),
                    "requirement_type": question.get("role"),
                    "source_ids": list(as_list(question.get("source_ids", []))),
                    "population": contract.get("population", ""),
                    "grain": contract.get("primary_grain", ""),
                    "scope": {},
                    "denominator": "",
                    "measure_or_fields": list(as_list(question.get("metric_ids", []))),
                    "method": question.get("method", ""),
                    "validation_rules": list(as_list(question.get("validation_rules", []))),
                    "status": "unresolved",
                }
            )
    migrated["analysis_blueprint"] = {
        "status": "draft",
        "context_required": any(item.get("role") == "context" for item in as_list(tree.get("questions", [])) if isinstance(item, dict)),
        "context_rationale": "Migrated context branch; necessity must be reviewed before contract approval.",
        "conditional_routes": [],
        "data_plan": data_plan,
        "stop_rule": "",
    }

    migrated["quality_checks"] = []
    if not isinstance(migrated.get("metrics"), list):
        migrated["metrics"] = []
    for metric in migrated.get("metrics", []):
        if not isinstance(metric, dict):
            continue
        if metric.get("status") in {"validated", "approved", "active"}:
            metric["legacy_status"] = metric.get("status")
            metric["status"] = "needs_validation"
        metric.setdefault("construct", "")
        metric.setdefault("measurement_limit", "")
        metric.setdefault("coverage", "")
        metric.setdefault("missingness", "")
        metric.setdefault("estimand", "")
        metric.setdefault("baseline", "")
        metric.setdefault("time_logic", "")
        metric.setdefault("uncertainty_method", "")
        metric.setdefault("sensitivity_checks", [])
        metric.setdefault("permitted_claim_types", [])

    if not isinstance(migrated.get("claims"), list):
        migrated["claims"] = []
    for claim in migrated.get("claims", []):
        if not isinstance(claim, dict):
            continue
        legacy_status = claim.get("status")
        if legacy_status in {"validated", "approved"}:
            claim["legacy_status"] = legacy_status
            claim["status"] = "candidate"
            claim["evidence_posture"] = "needs_validation"
            claim["stale_reason"] = "v2 migration requires quality and measurement-context review"
        claim.setdefault("claim_type", UNRESOLVED_CLAIM_TYPE)
        claim.setdefault("temporal_scope", "unknown")
        claim.setdefault("population", "")
        claim.setdefault("denominator", "")
        claim.setdefault("coverage", "")
        claim.setdefault("missingness", "")
        claim.setdefault("uncertainty", "")
        claim.setdefault("alternative_explanations", [])
        claim.setdefault("decision_use", "")
        claim.setdefault("quality_check_refs", [])

    if not isinstance(migrated.get("visuals"), list):
        migrated["visuals"] = []
    for visual in migrated.get("visuals", []):
        if not isinstance(visual, dict):
            continue
        visual["legacy_qa_status"] = visual.get("qa_status")
        visual["qa_status"] = "pending"
        if visual.get("intended_use", "stakeholder") in STAKEHOLDER_VISUAL_USES:
            visual["legacy_intended_use"] = visual.get("intended_use", "stakeholder")
            visual["intended_use"] = "draft"
        visual.setdefault("selection_rationale", "")
        visual.setdefault("variety_role", "not_applicable")
        visual.setdefault("quality_check_refs", [])
        visual["measurement_card"] = {field: "" for field in MEASUREMENT_CARD_FIELDS}
        visual["wording_review"] = {
            "audience": "",
            "language": "",
            "terminology_source": "",
            "plain_language_passed": False,
            "fact_interpretation_recommendation_separated": False,
            "notes": "",
        }

    if not isinstance(migrated.get("recommendations"), list):
        migrated["recommendations"] = []
    for recommendation in migrated.get("recommendations", []):
        if not isinstance(recommendation, dict):
            continue
        for field, default in (
            ("hypothesis", ""),
            ("expected_mechanism", ""),
            ("target_population", ""),
            ("success_metrics", []),
            ("guardrails", []),
            ("implementation_requirement", ""),
            ("owner", ""),
            ("revisit_condition", ""),
        ):
            recommendation.setdefault(field, default)

    if not isinstance(migrated.get("artifacts"), list):
        migrated["artifacts"] = []
    for artifact in migrated.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        if artifact.get("status") == "active":
            artifact["legacy_status"] = "active"
            artifact["status"] = "stale"

    migrated["analysis_brief"] = {
        "answer_status": "not_started",
        "business_question": discovery.get("selected_framing", ""),
        "executive_answer": "",
        "key_claim_ids": [],
        "interpretation": "",
        "alternative_explanations": [],
        "limitations": [],
        "unknowns": ["Migrated evidence and claims require v2 review."],
        "recommended_next_action": "Review the migrated contract, evidence, and claim posture.",
        "methods_refs": [],
    }

    changes = migrated.get("changes")
    if not isinstance(changes, list):
        changes = []
        migrated["changes"] = changes
    changes.append(
        {
            "change_id": "MIGRATION-V2",
            "type": "schema_migration",
            "from": "1.0",
            "to": "2.0",
            "reason": "Adopt reasoning-first blueprint, quality gates, and measurement context.",
            "status": "requires_review",
        }
    )
    return migrated


def add_fingerprint_hashes(data: dict[str, Any]) -> int:
    changed = 0
    for metric in as_list(data.get("metrics", [])):
        if not isinstance(metric, dict):
            continue
        fingerprint = metric.get("definition_fingerprint")
        if not isinstance(fingerprint, dict):
            continue
        value = stable_hash(fingerprint)
        if metric.get("fingerprint_hash") != value:
            metric["fingerprint_hash"] = value
            changed += 1
    return changed


def current_metric_hashes(data: dict[str, Any]) -> dict[str, str]:
    return {
        str(metric.get("metric_id")): stable_hash(metric.get("definition_fingerprint"))
        for metric in as_list(data.get("metrics", []))
        if isinstance(metric, dict)
        and require_nonempty(metric.get("metric_id"))
        and isinstance(metric.get("definition_fingerprint"), dict)
    }


def fingerprint_mismatches(item: dict[str, Any], current: dict[str, str]) -> list[str]:
    snapshots = item.get("metric_fingerprints", {})
    if not isinstance(snapshots, dict):
        return []
    return [str(metric_id) for metric_id, value in snapshots.items() if current.get(str(metric_id)) != value]


def stale_artifacts(data: dict[str, Any], write: bool = False) -> tuple[list[str], int]:
    current = current_metric_hashes(data)
    stale: list[str] = []
    changed = 0
    for claim in as_list(data.get("claims", [])):
        if not isinstance(claim, dict):
            continue
        mismatches = fingerprint_mismatches(claim, current)
        if mismatches:
            claim_id = claim.get("claim_id", "<unknown>")
            stale.append(f"{claim_id}: {', '.join(mismatches)}")
            if write and claim.get("status") not in {"candidate", "rejected", "superseded"}:
                claim["status"] = "candidate"
                claim["evidence_posture"] = "needs_validation"
                claim["stale_reason"] = f"metric fingerprint changed: {', '.join(mismatches)}"
                changed += 1
    for artifact in as_list(data.get("artifacts", [])):
        if not isinstance(artifact, dict):
            continue
        mismatches = fingerprint_mismatches(artifact, current)
        if mismatches:
            artifact_id = artifact.get("artifact_id", "<unknown>")
            stale.append(f"{artifact_id}: {', '.join(mismatches)}")
            if write and artifact.get("status") not in {"stale", "superseded"}:
                artifact["status"] = "stale"
                artifact["stale_reason"] = f"metric fingerprint changed: {', '.join(mismatches)}"
                changed += 1
    return stale, changed


def iter_text_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in TEXT_SUFFIXES:
            yield root
        return
    try:
        candidates = root.rglob("*")
        for path in candidates:
            try:
                is_file = path.is_file()
            except OSError:
                continue
            if not is_file or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            yield path
    except OSError:
        return


def scan_path(root: Path) -> list[str]:
    findings: list[str] = []
    if not root.exists():
        return [f"{root}: path does not exist"]
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            findings.append(f"{path}: cannot read ({exc.__class__.__name__})")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path}:{line_number}: possible secret")
                    break
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path}:{line_number}: machine-specific absolute path")
                    break
    return findings


def _unique_text(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip() or value.strip() in result:
            continue
        result.append(value.strip())
    return result


def build_analysis_brief(data: dict[str, Any]) -> dict[str, Any]:
    """Build a decision-ready human view from governed manifest content."""

    explicit = data.get("analysis_brief") if isinstance(data.get("analysis_brief"), dict) else {}
    discovery = data.get("needs_discovery") if isinstance(data.get("needs_discovery"), dict) else {}
    questions = [item for item in as_list(data.get("question_tree", {}).get("questions", [])) if isinstance(item, dict)] if isinstance(data.get("question_tree"), dict) else []
    claims = [item for item in as_list(data.get("claims", [])) if isinstance(item, dict)]
    approved_claims = [item for item in claims if item.get("status") == "approved"]
    approved_by_id = {str(item.get("claim_id")): item for item in approved_claims if require_nonempty(item.get("claim_id"))}
    requested_claim_ids = [item for item in as_list(explicit.get("key_claim_ids", [])) if isinstance(item, str)]
    selected_claims = [approved_by_id[item] for item in requested_claim_ids if item in approved_by_id]
    if not selected_claims:
        selected_claims = approved_claims

    quality_exceptions = [
        item
        for item in as_list(data.get("quality_checks", []))
        if isinstance(item, dict) and item.get("status") in {"warning", "fail", "unknown"}
    ]
    blockers = [item for item in quality_exceptions if item.get("severity") == "critical" and item.get("status") in {"fail", "unknown"}]
    unanswered = [
        item
        for item in questions
        if item.get("role") in ACTIVE_QUESTION_ROLES and item.get("status") not in {"answered", "superseded"}
    ]

    business_question = str(explicit.get("business_question", "")).strip()
    if not business_question:
        business_question = str(discovery.get("inferred_business_need", "")).strip()
    if not business_question:
        business_question = next((str(item.get("text", "")).strip() for item in questions if item.get("role") == "decision"), "")
    if not business_question:
        business_question = "The decision question has not yet been defined."

    executive_answer = str(explicit.get("executive_answer", "")).strip()
    if not executive_answer and selected_claims:
        executive_answer = " ".join(str(item.get("statement", "")).strip() for item in selected_claims[:3] if require_nonempty(item.get("statement")))
    if not executive_answer:
        executive_answer = "The available evidence does not yet support a decision-ready answer."

    status = explicit.get("answer_status")
    if status not in ANALYSIS_BRIEF_STATUSES or status == "not_started":
        if selected_claims and not blockers and not unanswered:
            status = "complete"
        elif blockers and not selected_claims:
            status = "blocked"
        else:
            status = "incomplete"

    evidence_rows = [
        {
            "claim_id": str(claim.get("claim_id", "")),
            "statement": str(claim.get("statement", "")).strip(),
            "evidence_refs": [item for item in as_list(claim.get("evidence_refs", [])) if isinstance(item, str)],
            "metric_ids": [item for item in as_list(claim.get("metric_ids", [])) if isinstance(item, str)],
        }
        for claim in selected_claims
    ]

    limitations = _unique_text(
        [*as_list(explicit.get("limitations", []))]
        + [f"{item.get('check_id', 'quality check')}: {item.get('impact')}" for item in quality_exceptions if require_nonempty(item.get("impact"))]
        + [item.get("missingness") for item in selected_claims]
        + [item.get("uncertainty") for item in selected_claims]
    )
    unknowns = _unique_text(
        [*as_list(explicit.get("unknowns", []))]
        + [str(item.get("text", "")).strip() for item in unanswered]
        + [
            f"{item.get('check_id', 'quality check')}: {item.get('required_action')}"
            for item in quality_exceptions
            if item.get("status") in {"fail", "unknown"} and require_nonempty(item.get("required_action"))
        ]
    )
    if status in {"incomplete", "blocked"} and not unknowns:
        unknowns = ["The decision question or supporting evidence is not yet complete."]
    alternative_explanations = _unique_text(
        [*as_list(explicit.get("alternative_explanations", []))]
        + [value for claim in selected_claims for value in as_list(claim.get("alternative_explanations", []))]
    )

    interpretation = str(explicit.get("interpretation", "")).strip()
    if not interpretation:
        interpretation = (
            "The statements above are the strongest approved interpretation supported by the recorded evidence."
            if selected_claims
            else "Interpretation is deferred until the evidence and quality gaps are resolved."
        )
    next_action = str(explicit.get("recommended_next_action", "")).strip()
    if not next_action:
        recommendations = [item for item in as_list(data.get("recommendations", [])) if isinstance(item, dict)]
        next_action = next((str(item.get("action", "")).strip() for item in recommendations if require_nonempty(item.get("action"))), "")
    if not next_action:
        next_action = "Resolve the stated evidence gaps, then rerun the relevant analysis question."

    metric_refs = [
        str(metric.get("definition_fingerprint", {}).get("source_query_ref", "")).strip()
        for metric in as_list(data.get("metrics", []))
        if isinstance(metric, dict) and isinstance(metric.get("definition_fingerprint"), dict)
    ]
    methods_refs = _unique_text([*as_list(explicit.get("methods_refs", [])), *metric_refs])

    return {
        "analysis_id": str(data.get("analysis_id", "")).strip(),
        "answer_status": status,
        "business_question": business_question,
        "executive_answer": executive_answer,
        "key_evidence": evidence_rows,
        "interpretation": interpretation,
        "alternative_explanations": alternative_explanations,
        "limitations": limitations,
        "unknowns": unknowns,
        "recommended_next_action": next_action,
        "methods_refs": methods_refs,
    }


def render_analysis_brief(brief: dict[str, Any]) -> str:
    def bullets(values: Iterable[Any], fallback: str) -> str:
        rows = [f"- {value}" for value in values if require_nonempty(value)]
        return "\n".join(rows) if rows else f"- {fallback}"

    evidence = [
        f"{item.get('claim_id', 'claim')}: {item.get('statement', '')} "
        f"(evidence: {', '.join(item.get('evidence_refs', [])) or 'not recorded'}; "
        f"metrics: {', '.join(item.get('metric_ids', [])) or 'not recorded'})"
        for item in as_list(brief.get("key_evidence", []))
        if isinstance(item, dict)
    ]
    return (
        f"# Analysis Brief: {brief.get('analysis_id') or 'Untitled analysis'}\n\n"
        f"**Answer status:** {str(brief.get('answer_status', 'incomplete')).replace('_', ' ').title()}\n\n"
        f"## Business question\n\n{brief.get('business_question', '')}\n\n"
        f"## Executive answer\n\n{brief.get('executive_answer', '')}\n\n"
        f"## Evidence supporting the answer\n\n{bullets(evidence, 'No approved evidence is available yet.')}\n\n"
        f"## Interpretation\n\n{brief.get('interpretation', '')}\n\n"
        f"## Alternative explanations\n\n{bullets(as_list(brief.get('alternative_explanations', [])), 'None recorded.')}\n\n"
        f"## Limitations\n\n{bullets(as_list(brief.get('limitations', [])), 'No material limitation recorded.')}\n\n"
        f"## What remains unknown\n\n{bullets(as_list(brief.get('unknowns', [])), 'No material unknown recorded.')}\n\n"
        f"## Recommended next action\n\n{brief.get('recommended_next_action', '')}\n\n"
        f"## Methods and traceability\n\n{bullets(as_list(brief.get('methods_refs', [])), 'See the analysis manifest.')}\n"
    )


def command_init(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "analysis-manifest.json"
    if manifest_path.exists() and not args.force:
        if _json_output(args):
            _emit_json({"command": "init", "passed": False, "error": f"manifest already exists: {manifest_path}"})
        else:
            print(f"ERROR: manifest already exists: {manifest_path}", file=sys.stderr)
        return 1
    data = load_json(TEMPLATE)
    data["analysis_id"] = args.analysis_id
    write_json_atomic(manifest_path, data)
    (output / "evidence").mkdir(exist_ok=True)
    brief_path = output / "analysis-brief.md"
    if not brief_path.exists():
        brief_path.write_text(render_analysis_brief(build_analysis_brief(data)), encoding="utf-8", newline="\n")
    if _json_output(args):
        _emit_json(
            {
                "command": "init",
                "passed": True,
                "analysis_id": args.analysis_id,
                "manifest": str(manifest_path),
                "analysis_brief": str(brief_path),
            }
        )
    else:
        print(f"Created {manifest_path}")
        print(f"Created {brief_path}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "validate", "passed": False, "load_error": str(exc), "errors": []})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(data, strict=args.strict, stage=args.stage)
    payload = {"command": "validate", "passed": not errors, "stage": args.stage, "strict": args.strict, "errors": errors}
    if _json_output(args):
        _emit_json(payload)
        return 1 if errors else 0
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Manifest validation: FAIL ({len(errors)} error(s))")
        return 1
    print("Manifest validation: PASS")
    return 0


def command_quality(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "quality", "passed": False, "load_error": str(exc)})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(data)
    if errors:
        if _json_output(args):
            _emit_json({"command": "quality", "passed": False, "manifest_errors": errors})
            return 1
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Quality gate: INVALID MANIFEST ({len(errors)} error(s))")
        return 1

    checks = [item for item in as_list(data.get("quality_checks", [])) if isinstance(item, dict)]
    counts = {status: 0 for status in sorted(QUALITY_STATUSES)}
    for check in checks:
        if check.get("status") in counts:
            counts[str(check.get("status"))] += 1
    _, blockers, warnings = _quality_gate_state(data)
    passed = not blockers and not (warnings and getattr(args, "fail_on_warning", False))
    if _json_output(args):
        _emit_json(
            {
                "command": "quality",
                "passed": passed,
                "counts": counts,
                "blockers": blockers,
                "warnings": warnings,
            }
        )
        return 0 if passed else 1
    print("Quality checks: " + ", ".join(f"{status}={counts[status]}" for status in sorted(counts)))
    if blockers:
        for check_id in blockers:
            print(f"BLOCKER: {check_id}")
        print(f"Quality gate: FAIL ({len(blockers)} critical blocker(s))")
        return 1
    if warnings:
        for check_id in warnings:
            print(f"WARNING: {check_id}")
        if args.fail_on_warning:
            print(f"Quality gate: FAIL ({len(warnings)} warning(s))")
            return 1
    print("Quality gate: PASS")
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
        migrated = migrate_v1_manifest(data)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "migrate", "passed": False, "load_error": str(exc)})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.write:
        output = args.manifest
    elif args.output is not None:
        output = args.output
    else:
        output = args.manifest.with_name(f"{args.manifest.stem}.v2{args.manifest.suffix}")
    same_path = output.resolve() == args.manifest.resolve()
    if same_path and not args.write:
        message = "migration output resolves to the source manifest; use --write for explicit in-place replacement"
        if _json_output(args):
            _emit_json({"command": "migrate", "passed": False, "error": message})
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    if output.exists() and not same_path and not args.force:
        message = f"migration output already exists: {output}; use --force to replace it"
        if _json_output(args):
            _emit_json({"command": "migrate", "passed": False, "error": message})
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    write_json_atomic(output, migrated)
    migrated_from = str(data.get("schema_version"))
    if _json_output(args):
        _emit_json(
            {
                "command": "migrate",
                "passed": True,
                "from_schema": migrated_from,
                "to_schema": "2.0",
                "output": str(output.resolve()),
                "review_required": migrated_from != "2.0",
            }
        )
        return 0
    if data.get("schema_version") == "2.0":
        print(f"Manifest already uses schema 2.0; wrote unchanged copy to {output}")
    else:
        print(f"Migrated schema 1.0 to 2.0: {output}")
        print("Legacy approvals were demoted and unresolved v2 requirements remain for review.")
    return 0


def command_fingerprint(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "fingerprint", "passed": False, "load_error": str(exc)})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    input_errors = collection_shape_errors(data, ("metrics",))
    for index, metric in enumerate(as_list(data.get("metrics", []))):
        if isinstance(metric, dict) and not isinstance(metric.get("definition_fingerprint"), dict):
            input_errors.append(f"metrics[{index}] missing definition_fingerprint")
    if input_errors:
        if _json_output(args):
            _emit_json({"command": "fingerprint", "passed": False, "errors": input_errors})
        else:
            for error in input_errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"Fingerprint update: FAIL ({len(input_errors)} error(s))")
        return 1
    changed = add_fingerprint_hashes(data)
    if args.write:
        write_json_atomic(args.manifest, data)
    fingerprints: dict[str, str] = {}
    for metric in as_list(data.get("metrics", [])):
        if not isinstance(metric, dict):
            continue
        if metric.get("fingerprint_hash"):
            fingerprints[str(metric.get("metric_id", "<unknown>"))] = str(metric["fingerprint_hash"])
    if _json_output(args):
        _emit_json(
            {
                "command": "fingerprint",
                "passed": True,
                "algorithm": FINGERPRINT_ALGORITHM,
                "canonicalization": "JSON sorted keys, compact separators, ASCII escapes, UTF-8 bytes",
                "fingerprints": fingerprints,
                "changes": changed,
                "written": bool(args.write),
            }
        )
        return 0
    for metric_id, fingerprint_hash in fingerprints.items():
        print(f"{metric_id}: {fingerprint_hash}")
    print(f"Fingerprint update: {changed} change(s){' written' if args.write else ' calculated'}")
    return 0


def command_stale(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "stale", "passed": False, "load_error": str(exc)})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    input_errors = collection_shape_errors(data, ("metrics", "claims", "artifacts"))
    if input_errors:
        if _json_output(args):
            _emit_json({"command": "stale", "passed": False, "errors": input_errors})
        else:
            for error in input_errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"Stale check: INVALID MANIFEST ({len(input_errors)} error(s))")
        return 1
    stale, changed = stale_artifacts(data, write=args.write)
    if args.write and changed:
        write_json_atomic(args.manifest, data)
    passed = not stale
    if _json_output(args):
        _emit_json(
            {
                "command": "stale",
                "passed": passed,
                "stale": stale,
                "updated": changed,
                "written": bool(args.write),
            }
        )
        return 1 if stale and args.fail_on_stale else 0
    if stale:
        for item in stale:
            print(f"STALE: {item}")
        print(f"Stale check: FOUND ({len(stale)} artifact(s), {changed} updated)")
        return 1 if args.fail_on_stale else 0
    print("Stale check: PASS")
    return 0


def command_scan(args: argparse.Namespace) -> int:
    findings = scan_path(args.path.resolve())
    if _json_output(args):
        _emit_json({"command": "scan", "passed": not findings, "path": str(args.path.resolve()), "findings": findings})
        return 1 if findings else 0
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}", file=sys.stderr)
        print(f"Portability scan: FAIL ({len(findings)} finding(s))")
        return 1
    print("Portability scan: PASS")
    return 0


def _evaluate_gate(
    data: dict[str, Any],
    *,
    stage: str,
    scan_root: Path,
    fail_on_warning: bool = False,
) -> dict[str, Any]:
    validation_errors = validate_manifest(data, stage=stage)
    _, blockers, warnings = _quality_gate_state(data)
    stale, _ = stale_artifacts(data)
    portability_findings = scan_path(scan_root.resolve())
    passed = not validation_errors and not blockers and not stale and not portability_findings
    if fail_on_warning and warnings:
        passed = False
    return {
        "passed": passed,
        "stage": stage,
        "validation_errors": validation_errors,
        "quality_blockers": blockers,
        "quality_warnings": warnings,
        "stale_dependencies": stale,
        "portability_findings": portability_findings,
    }


def command_brief(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json(
                {
                    "command": "brief",
                    "generated": False,
                    "analysis_ready": False,
                    "delivery_ready": False,
                    "load_error": str(exc),
                }
            )
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_manifest(data)
    if errors:
        if _json_output(args):
            _emit_json(
                {
                    "command": "brief",
                    "generated": False,
                    "analysis_ready": False,
                    "delivery_ready": False,
                    "manifest_errors": errors,
                }
            )
        else:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"Analysis brief: INVALID MANIFEST ({len(errors)} error(s))")
        return 1
    brief = build_analysis_brief(data)
    rendered = render_analysis_brief(brief)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    analysis_validation_errors = validate_manifest(data, stage="claims")
    _, analysis_blockers, analysis_warnings = _quality_gate_state(data)
    analysis_ready = not analysis_validation_errors and not analysis_blockers
    delivery = _evaluate_gate(data, stage="delivery", scan_root=args.manifest.parent)
    if _json_output(args):
        _emit_json(
            {
                "command": "brief",
                "generated": True,
                "answer_status": brief["answer_status"],
                "analysis_ready": analysis_ready,
                "delivery_ready": delivery["passed"],
                "output": str(args.output.resolve()) if args.output else None,
                "analysis": {
                    "validation_errors": analysis_validation_errors,
                    "quality_blockers": analysis_blockers,
                    "quality_warnings": analysis_warnings,
                },
                "delivery": delivery,
                "brief": brief,
            }
        )
    elif args.output is not None:
        print(f"Created {args.output.resolve()}")
    else:
        print(rendered, end="")
    return 0


def command_gate(args: argparse.Namespace) -> int:
    try:
        data = load_json(args.manifest)
    except ManifestError as exc:
        if _json_output(args):
            _emit_json({"command": "gate", "passed": False, "load_error": str(exc)})
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    scan_root = (args.scan_path if args.scan_path is not None else args.manifest.parent).resolve()
    payload = {
        "command": "gate",
        **_evaluate_gate(
            data,
            stage=args.stage,
            scan_root=scan_root,
            fail_on_warning=args.fail_on_warning,
        ),
    }
    if _json_output(args):
        _emit_json(payload)
    else:
        for error in payload["validation_errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        for item in payload["quality_blockers"]:
            print(f"BLOCKER: {item}")
        for item in payload["quality_warnings"]:
            print(f"WARNING: {item}")
        for item in payload["stale_dependencies"]:
            print(f"STALE: {item}")
        for item in payload["portability_findings"]:
            print(f"ERROR: {item}", file=sys.stderr)
        print("Analysis gate: PASS" if payload["passed"] else "Analysis gate: FAIL")
    return 0 if payload["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_format_option(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--format", choices=("text", "json"), default="text")

    init_parser = subparsers.add_parser("init", help="create an analysis folder and manifest")
    init_parser.add_argument("output", type=Path)
    init_parser.add_argument("--analysis-id", required=True)
    init_parser.add_argument("--force", action="store_true")
    add_format_option(init_parser)
    init_parser.set_defaults(func=command_init)

    validate_parser = subparsers.add_parser("validate", help="validate manifest structure and governance")
    validate_parser.add_argument("manifest", type=Path)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--stage", choices=sorted(VALIDATION_STAGES))
    add_format_option(validate_parser)
    validate_parser.set_defaults(func=command_validate)

    quality_parser = subparsers.add_parser("quality", help="summarise quality checks and enforce blockers")
    quality_parser.add_argument("manifest", type=Path)
    quality_parser.add_argument("--fail-on-warning", action="store_true")
    add_format_option(quality_parser)
    quality_parser.set_defaults(func=command_quality)

    migrate_parser = subparsers.add_parser("migrate", help="migrate a v1 manifest without inventing v2 approvals")
    migrate_parser.add_argument("manifest", type=Path)
    migrate_parser.add_argument("--output", type=Path)
    migrate_parser.add_argument("--write", action="store_true", help="replace the source manifest explicitly")
    migrate_parser.add_argument("--force", action="store_true", help="replace an existing separate output")
    add_format_option(migrate_parser)
    migrate_parser.set_defaults(func=command_migrate)

    fingerprint_parser = subparsers.add_parser("fingerprint", help="calculate metric fingerprint hashes")
    fingerprint_parser.add_argument("manifest", type=Path)
    fingerprint_parser.add_argument("--write", action="store_true")
    add_format_option(fingerprint_parser)
    fingerprint_parser.set_defaults(func=command_fingerprint)

    stale_parser = subparsers.add_parser("stale", help="detect artifacts with changed metric fingerprints")
    stale_parser.add_argument("manifest", type=Path)
    stale_parser.add_argument("--write", action="store_true")
    stale_parser.add_argument("--fail-on-stale", action="store_true")
    add_format_option(stale_parser)
    stale_parser.set_defaults(func=command_stale)

    scan_parser = subparsers.add_parser("scan", help="scan text files for secrets and machine paths")
    scan_parser.add_argument("path", type=Path)
    add_format_option(scan_parser)
    scan_parser.set_defaults(func=command_scan)

    brief_parser = subparsers.add_parser("brief", help="render a stakeholder-ready analysis brief")
    brief_parser.add_argument("manifest", type=Path)
    brief_parser.add_argument("--output", type=Path)
    add_format_option(brief_parser)
    brief_parser.set_defaults(func=command_brief)

    gate_parser = subparsers.add_parser("gate", help="run validation, quality, staleness, and portability checks once")
    gate_parser.add_argument("manifest", type=Path)
    gate_parser.add_argument("--stage", choices=sorted(VALIDATION_STAGES), default="delivery")
    gate_parser.add_argument("--scan-path", type=Path)
    gate_parser.add_argument("--fail-on-warning", action="store_true")
    add_format_option(gate_parser)
    gate_parser.set_defaults(func=command_gate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
