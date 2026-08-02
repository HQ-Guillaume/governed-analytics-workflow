from __future__ import annotations

import copy
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "analysis_guard.py"
SPEC = importlib.util.spec_from_file_location("analysis_guard", MODULE_PATH)
assert SPEC and SPEC.loader
analysis_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis_guard)


def quality_check(category: str, status: str = "pass", severity: str = "critical") -> dict:
    return {
        "check_id": f"QC-{category}",
        "category": category,
        "condition": "always" if category in analysis_guard.ALWAYS_QUALITY_CATEGORIES else "conditional",
        "status": status,
        "severity": severity,
        "question_ids": ["Q1"],
        "source_ids": ["S1"],
        "metric_ids": ["M1"],
        "evidence_ref": f"evidence/quality/{category}.json",
        "impact": "No material limitation found." if status == "pass" else "The result may be unreliable.",
        "required_action": "None." if status == "pass" else "Resolve or carry the limitation into claims.",
        "checked_at": "2026-02-01",
    }


def valid_manifest() -> dict:
    data = json.loads((ROOT / "assets" / "analysis-manifest.template.json").read_text(encoding="utf-8"))
    data["analysis_id"] = "2026-01-01-generic-analysis"
    data["status"] = "ready_for_delivery"
    data["needs_discovery"].update(
        {
            "triggers": ["metric-led request"],
            "stated_request": [{"request_item_id": "RQ1", "text": "Describe the complete distribution."}],
            "request_decomposition": {
                "facts": [],
                "objectives": ["Establish a complete baseline before prioritising investigation."],
                "constraints": [],
                "hypotheses": [],
                "suggested_metrics": ["Completion total"],
                "suggested_methods": [],
                "suggested_solutions": [],
                "output_preferences": [],
                "uncertainties": ["The requested total may hide the exclusive state distribution."],
            },
            "inferred_business_need": "Support a prioritisation decision with a complete baseline.",
            "decision": {
                "decision_id": "D1",
                "statement": "Decide which state needs investigation first.",
                "owner": "decision owner",
                "options": ["investigate", "monitor"],
                "deadline_or_revisit": "2026-02-15",
                "consequence_of_error": "Effort may be directed to the wrong state.",
            },
            "selected_framing": "Measure the exclusive state distribution before prioritising action.",
            "framing_rationale": "The requested total alone cannot reveal which state drives the decision.",
            "framing_confidence": "high",
            "construct_checks": ["Maximum state represents progression, not repeated activity."],
            "context_needs": ["Population size validates the denominator."],
            "evidence_ceiling": "Descriptive and associative claims only.",
            "permitted_claim_types": ["descriptive", "associative"],
            "framing_status": "confirmed",
            "user_decision_required": False,
        }
    )
    data["analysis_blueprint"] = {
        "status": "operational",
        "context_required": False,
        "context_rationale": "The eligible-population denominator is defined in the decision branch; no separate context branch is needed.",
        "conditional_routes": [
            {
                "route": "ambiguity",
                "trigger": "The request proposed a total without defining the decision.",
                "rationale": "Alternative framing was needed before measurement.",
                "applied": True,
            }
        ],
        "data_plan": [
            {
                "data_requirement_id": "DR1",
                "question_ids": ["Q1"],
                "purpose": "Estimate the complete exclusive distribution.",
                "requirement_type": "decision",
                "source_ids": ["S1"],
                "population": "Eligible entities",
                "grain": "entity",
                "scope": {"market": "all"},
                "denominator": "Distinct eligible entities",
                "measure_or_fields": ["maximum_state", "entity_id"],
                "method": "Assign one maximum state to each eligible entity.",
                "validation_rules": ["Retain the zero state and reconcile the denominator."],
                "status": "validated",
            }
        ],
        "stop_rule": "Stop when all states reconcile to the eligible population and the claim is reviewed.",
    }
    data["question_tree"].update(
        {
            "status": "operational",
            "primary_problem_type": "find_patterns",
            "secondary_problem_types": [],
            "questions": [
                {
                    "question_id": "Q1",
                    "parent_id": None,
                    "text": "How is the eligible population distributed across exclusive states?",
                    "role": "decision",
                    "purpose": "Provide the baseline required for prioritisation.",
                    "problem_type": "find_patterns",
                    "decision_relevance": "Shows which state contains the largest eligible group.",
                    "source_ids": ["S1"],
                    "data_requirement_ids": ["DR1"],
                    "metric_ids": ["M1"],
                    "population": "Eligible entities",
                    "grain": "entity",
                    "method": "Exclusive distribution.",
                    "validation_rules": ["Complete expected domain."],
                    "expected_output": "Reviewed distribution with denominator and uncertainty limits.",
                    "status": "answered",
                }
            ],
            "coverage": [
                {
                    "request_item_id": "RQ1",
                    "disposition": "answered_by_question",
                    "question_ids": ["Q1"],
                    "reason": "",
                }
            ],
        }
    )
    data["contract"].update(
        {
            "status": "approved",
            "risk": "medium",
            "audience": ["decision team"],
            "owner": "analysis owner",
            "population": "Eligible entities",
            "period": {"start": "2026-01-01", "end": "2026-01-31", "timezone": "UTC"},
            "primary_grain": "entity",
            "claim_limits": ["No causal interpretation."],
            "definition_of_done": "The decision question has an approved, reproducible claim.",
            "approval_gates": ["claim promotion", "stakeholder delivery"],
        }
    )
    data["sources"] = [
        {
            "source_id": "S1",
            "name": "Canonical source",
            "owner": "source owner",
            "authority": "canonical",
            "source_grain": "event",
            "coverage": "Eligible population",
            "freshness": {"valid_as_of": "2026-01-31", "revalidate_after": "2026-02-28"},
            "join_keys": ["entity_id"],
            "joinability": "direct",
            "allowed_uses": ["population metrics"],
            "forbidden_uses": ["causal claims"],
            "access_and_pii": "No personal data exported.",
            "caveats": [],
        }
    ]
    fingerprint = {
        "population": "Eligible entities",
        "calculation_grain": "entity",
        "time_window": {"start": "2026-01-01", "end": "2026-01-31", "timezone": "UTC"},
        "scope": {"market": "all"},
        "filters": ["valid_record = true"],
        "numerator": "Distinct eligible entities in the state",
        "denominator": "Distinct eligible entities",
        "deduplication": "One maximum state per entity",
        "source_query_ref": "evidence/query.sql",
        "run_date": "2026-02-01",
    }
    fingerprint_hash = analysis_guard.stable_hash(fingerprint)
    data["metrics"] = [
        {
            "metric_id": "M1",
            "name": "Maximum observed state",
            "question_ids": ["Q1"],
            "source_ids": ["S1"],
            "metric_shape": "exclusive_distribution",
            "status": "validated",
            "construct": "Furthest state reached by an eligible entity.",
            "measurement_limit": "Does not measure attention within a state.",
            "coverage": "All eligible entities in the canonical source.",
            "missingness": "Missing state is assigned to zero only after eligibility is verified.",
            "estimand": "Share of eligible entities in each exclusive maximum state.",
            "baseline": "All eligible entities, including zero state.",
            "time_logic": "Maximum observed state during the analysis period.",
            "uncertainty_method": "Descriptive census; report coverage and counts.",
            "sensitivity_checks": ["Recalculate under a narrower eligibility definition."],
            "permitted_claim_types": ["descriptive"],
            "expected_domain": [0, 20, 40, 60, 80, 100],
            "observed_domain": [0, 20, 40, 60, 80, 100],
            "definition_fingerprint": fingerprint,
            "fingerprint_hash": fingerprint_hash,
        }
    ]
    data["quality_checks"] = [quality_check(category) for category in sorted(analysis_guard.ALWAYS_QUALITY_CATEGORIES)]
    data["evidence"] = [
        {
            "evidence_id": "E1",
            "question_ids": ["Q1"],
            "source_ids": ["S1"],
            "result_ref": "evidence/result.csv",
            "status": "validated",
        }
    ]
    data["claims"] = [
        {
            "claim_id": "C1",
            "question_ids": ["Q1"],
            "statement": "The eligible population spans the complete expected state domain.",
            "status": "approved",
            "evidence_posture": "verified",
            "claim_type": "descriptive",
            "temporal_scope": "full_period",
            "population": "Eligible entities",
            "denominator": "Distinct eligible entities",
            "coverage": "All eligible entities in the canonical source.",
            "missingness": "Missing state handled under the documented zero-state rule.",
            "uncertainty": "Descriptive census; source coverage remains the main limitation.",
            "alternative_explanations": [],
            "decision_use": "Establish the baseline for prioritisation.",
            "evidence_refs": ["E1"],
            "metric_ids": ["M1"],
            "quality_check_refs": [],
            "metric_fingerprints": {"M1": fingerprint_hash},
            "valid_as_of": "2026-01-31",
            "caveats": [],
            "owner": "analyst",
            "approved_by": "reviewer",
            "approved_at": "2026-02-02",
            "supersedes": [],
        }
    ]
    data["visuals"] = [
        {
            "visual_id": "V1",
            "claim_ids": ["C1"],
            "question_id": "Q1",
            "result_ref": "evidence/result.csv",
            "message": "Every expected state is represented in the eligible population.",
            "communication_function": "distribution",
            "data_structure": {"metric_shape": "exclusive_distribution", "ordered": True},
            "candidate_charts": ["ordered_bar"],
            "selected_chart": "ordered_bar",
            "selection_rationale": "Ordered bars preserve the exclusive categories and a common baseline.",
            "variety_role": "not_applicable",
            "rejected_alternatives": ["funnel"],
            "required_labels": ["population", "denominator", "period"],
            "live_catalogue_checked": True,
            "catalogue_check_note": "Distribution function reviewed once for this output.",
            "quality_check_refs": [],
            "measurement_card": {
                "population": "Eligible entities",
                "grain": "entity",
                "period": "2026-01-01 to 2026-01-31 UTC",
                "denominator": "Distinct eligible entities",
                "coverage": "All eligible entities in the canonical source.",
                "unit": "share of entities",
                "temporal_scope": "full period",
                "missing_zero_treatment": "Verified missing states are assigned to zero.",
                "claim_posture": "descriptive, verified",
                "source_ref": "S1 / M1",
            },
            "wording_review": {
                "audience": "Non-specialist decision team",
                "language": "English",
                "terminology_source": "Approved business glossary",
                "plain_language_passed": True,
                "fact_interpretation_recommendation_separated": True,
                "notes": "Labels name the measured states directly.",
            },
            "intended_use": "stakeholder",
            "qa_status": "passed",
        }
    ]
    data["recommendations"] = [
        {
            "recommendation_id": "REC1",
            "decision_id": "D1",
            "supporting_claim_ids": ["C1"],
            "hypothesis": "The largest state is the best starting point for diagnostic work.",
            "expected_mechanism": "Prioritising the largest state maximises the population addressed first.",
            "target_population": "Eligible entities in the largest state.",
            "action": "Investigate the largest state before selecting an intervention.",
            "success_metrics": ["Validated diagnostic coverage"],
            "guardrails": ["Do not infer causality from the distribution."],
            "implementation_requirement": "Assign an owner and preserve the same population definition.",
            "owner": "decision owner",
            "revisit_condition": "Revisit if eligibility or state tracking changes.",
        }
    ]
    data["analysis_brief"] = {
        "answer_status": "complete",
        "business_question": "Which state should be investigated first?",
        "executive_answer": "The expected state domain is complete; prioritize diagnosis using the largest state.",
        "key_claim_ids": ["C1"],
        "interpretation": "The distribution is suitable for prioritizing a diagnostic investigation, not for causal action.",
        "alternative_explanations": [],
        "limitations": ["The distribution does not explain why entities are in each state."],
        "unknowns": [],
        "recommended_next_action": "Investigate the largest state before selecting an intervention.",
        "methods_refs": ["evidence/query.sql"],
    }
    data["artifacts"] = [
        {
            "artifact_id": "A1",
            "purpose": "stakeholder brief",
            "path": "stakeholder-brief.pptx",
            "status": "active",
            "depends_on": ["M1", "C1", "V1"],
            "metric_fingerprints": {"M1": fingerprint_hash},
        }
    ]
    return data


def legacy_manifest() -> dict:
    data = valid_manifest()
    data["schema_version"] = "1.0"
    data["needs_discovery"]["mode"] = "deep"
    data.pop("analysis_blueprint")
    data.pop("quality_checks")
    data.pop("analysis_brief")
    for field in (
        "request_decomposition",
        "selected_framing",
        "framing_rationale",
        "framing_confidence",
        "construct_checks",
        "context_needs",
        "permitted_claim_types",
        "user_decision_required",
    ):
        data["needs_discovery"].pop(field, None)
    question = data["question_tree"]["questions"][0]
    question["role"] = "core"
    question.pop("purpose", None)
    question.pop("population", None)
    question.pop("grain", None)
    question.pop("data_requirement_ids", None)
    for field in (
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
    ):
        data["metrics"][0].pop(field, None)
    for field in (
        "claim_type",
        "temporal_scope",
        "population",
        "denominator",
        "coverage",
        "missingness",
        "uncertainty",
        "quality_check_refs",
    ):
        data["claims"][0].pop(field, None)
    for field in ("selection_rationale", "variety_role", "quality_check_refs", "measurement_card", "wording_review"):
        data["visuals"][0].pop(field, None)
    return data


class ManifestValidationTest(unittest.TestCase):
    def test_template_passes_non_stage_validation(self) -> None:
        template = analysis_guard.load_json(ROOT / "assets" / "analysis-manifest.template.json")
        self.assertEqual([], analysis_guard.validate_manifest(template))
        brief = analysis_guard.build_analysis_brief(template)
        self.assertEqual("incomplete", brief["answer_status"])
        self.assertTrue(brief["unknowns"])

    def test_complete_manifest_passes_every_stage(self) -> None:
        for stage in ("contract", "evidence", "claims", "delivery"):
            with self.subTest(stage=stage):
                self.assertEqual([], analysis_guard.validate_manifest(valid_manifest(), stage=stage))
        self.assertEqual([], analysis_guard.validate_manifest(valid_manifest(), strict=True))

    def test_invalid_stage_is_rejected(self) -> None:
        self.assertIn("invalid validation stage", analysis_guard.validate_manifest(valid_manifest(), stage="unknown")[0])

    def test_missing_zero_or_expected_class_is_rejected(self) -> None:
        data = valid_manifest()
        data["metrics"][0]["observed_domain"] = [20, 40, 60, 80, 100]
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("missing expected values: [0]" in error for error in errors), errors)

    def test_exclusive_distribution_cannot_use_funnel(self) -> None:
        data = valid_manifest()
        data["visuals"][0]["selected_chart"] = "funnel"
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("cannot use a funnel" in error for error in errors), errors)

    def test_claim_cannot_exceed_evidence_ceiling(self) -> None:
        data = valid_manifest()
        data["claims"][0]["claim_type"] = "causal"
        data["metrics"][0]["permitted_claim_types"] = ["descriptive", "causal"]
        data["claims"][0]["causal_design_ref"] = "evidence/design.md"
        errors = analysis_guard.validate_manifest(data, stage="claims")
        self.assertTrue(any("exceeds the needs-discovery evidence ceiling" in error for error in errors), errors)

    def test_stakeholder_visual_requires_approved_claim(self) -> None:
        data = valid_manifest()
        data["claims"][0]["status"] = "validated"
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("uses non-approved claim" in error for error in errors), errors)

    def test_approved_claim_requires_approval_metadata(self) -> None:
        data = valid_manifest()
        data["claims"][0]["approved_by"] = ""
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("approved_by and approved_at" in error for error in errors), errors)

    def test_changed_fingerprint_marks_dependencies_stale(self) -> None:
        data = valid_manifest()
        data["metrics"][0]["definition_fingerprint"]["population"] = "Changed population"
        stale, changed = analysis_guard.stale_artifacts(data, write=True)
        self.assertEqual(2, len(stale))
        self.assertEqual(2, changed)
        self.assertEqual("candidate", data["claims"][0]["status"])
        self.assertEqual("needs_validation", data["claims"][0]["evidence_posture"])
        self.assertEqual("stale", data["artifacts"][0]["status"])

    def test_comparison_requires_compatible_fingerprints_or_rationale(self) -> None:
        data = valid_manifest()
        second = copy.deepcopy(data["metrics"][0])
        second["metric_id"] = "M2"
        second["definition_fingerprint"]["population"] = "Different population"
        second["fingerprint_hash"] = analysis_guard.stable_hash(second["definition_fingerprint"])
        data["metrics"].append(second)
        data["claims"][0]["comparison_metric_ids"] = ["M1", "M2"]
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("incompatible fingerprints without rationale" in error for error in errors), errors)

    def test_validated_claim_requires_metric_snapshot(self) -> None:
        data = valid_manifest()
        data["claims"][0]["metric_fingerprints"] = {}
        errors = analysis_guard.validate_manifest(data, stage="claims")
        self.assertTrue(any("missing metric fingerprint snapshots" in error for error in errors), errors)

    def test_active_artifact_requires_transitive_metric_snapshot(self) -> None:
        data = valid_manifest()
        data["artifacts"][0]["depends_on"] = ["C1", "V1"]
        data["artifacts"][0]["metric_fingerprints"] = {}
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("missing metric fingerprint snapshots" in error for error in errors), errors)

    def test_request_coverage_must_include_every_stated_item(self) -> None:
        data = valid_manifest()
        data["question_tree"]["coverage"] = []
        errors = analysis_guard.validate_manifest(data, stage="contract")
        self.assertTrue(any("request coverage missing stated items" in error for error in errors), errors)

    def test_active_question_requires_bidirectional_data_plan(self) -> None:
        data = valid_manifest()
        data["analysis_blueprint"]["data_plan"][0]["question_ids"] = []
        errors = analysis_guard.validate_manifest(data, stage="contract")
        self.assertTrue(any("incomplete data requirement" in error for error in errors), errors)

    def test_contract_requires_recorded_reasoning_and_decision_summary(self) -> None:
        data = valid_manifest()
        data["needs_discovery"]["request_decomposition"] = {
            field: [] for field in data["needs_discovery"]["request_decomposition"]
        }
        data["needs_discovery"]["decision"]["statement"] = ""
        data["analysis_blueprint"]["context_rationale"] = ""
        errors = analysis_guard.validate_manifest(data, stage="contract")
        self.assertTrue(any("concise request decomposition" in error for error in errors), errors)
        self.assertTrue(any("complete decision summary" in error for error in errors), errors)
        self.assertTrue(any("context_rationale" in error for error in errors), errors)

    def test_active_question_problem_type_must_be_declared(self) -> None:
        data = valid_manifest()
        data["question_tree"]["questions"][0]["problem_type"] = "categorise_things"
        errors = analysis_guard.validate_manifest(data, stage="contract")
        self.assertTrue(any("undeclared problem_type" in error for error in errors), errors)

    def test_evidence_stage_requires_all_always_on_quality_categories(self) -> None:
        data = valid_manifest()
        data["quality_checks"] = data["quality_checks"][1:]
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("missing always-on quality categories" in error for error in errors), errors)

    def test_evidence_stage_requires_complete_source_and_fingerprint_context(self) -> None:
        data = valid_manifest()
        data["sources"][0]["coverage"] = ""
        data["sources"][0]["freshness"]["valid_as_of"] = ""
        del data["metrics"][0]["definition_fingerprint"]["filters"]
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("incomplete source context" in error for error in errors), errors)
        self.assertTrue(any("freshness requires" in error for error in errors), errors)
        self.assertTrue(any("fingerprint missing fields: filters" in error for error in errors), errors)

    def test_completed_quality_check_requires_checked_at(self) -> None:
        data = valid_manifest()
        data["quality_checks"][0]["checked_at"] = ""
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("requires checked_at" in error for error in errors), errors)

    def test_route_activates_conditional_quality_checks(self) -> None:
        data = valid_manifest()
        data["analysis_blueprint"]["conditional_routes"].append(
            {
                "route": "outcome_comparison",
                "trigger": "The request compares entities with and without an outcome.",
                "rationale": "Ordering and composition can change the interpretation.",
                "applied": True,
            }
        )
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("route outcome_comparison missing conditional quality categories" in error for error in errors), errors)

    def test_critical_fail_or_unknown_blocks_claim_promotion(self) -> None:
        for status in ("fail", "unknown"):
            with self.subTest(status=status):
                data = valid_manifest()
                data["quality_checks"][0].update({"status": status, "impact": "Material risk.", "required_action": "Resolve."})
                errors = analysis_guard.validate_manifest(data, stage="claims")
                self.assertTrue(any("claim promotion blocked" in error for error in errors), errors)

    def test_quality_warning_must_follow_claim_and_visual(self) -> None:
        data = valid_manifest()
        warning_id = data["quality_checks"][0]["check_id"]
        data["quality_checks"][0].update({"status": "warning", "severity": "major"})
        errors = analysis_guard.validate_manifest(data, stage="claims")
        self.assertTrue(any("does not reference relevant quality warnings" in error for error in errors), errors)
        data["claims"][0]["quality_check_refs"] = [warning_id]
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("does not carry claim quality warnings" in error for error in errors), errors)

    def test_source_level_warning_must_follow_claim(self) -> None:
        data = valid_manifest()
        warning = data["quality_checks"][0]
        warning_id = warning["check_id"]
        warning.update({"status": "warning", "severity": "major", "question_ids": [], "metric_ids": []})
        errors = analysis_guard.validate_manifest(data, stage="claims")
        self.assertTrue(any(warning_id in error and "quality warnings" in error for error in errors), errors)

    def test_promoted_claim_requires_statement_and_resolved_type(self) -> None:
        data = valid_manifest()
        data["claims"][0]["statement"] = ""
        data["claims"][0]["claim_type"] = "unknown"
        errors = analysis_guard.validate_manifest(data, stage="claims")
        self.assertTrue(any("unresolved claim_type" in error for error in errors), errors)
        self.assertTrue(any("incomplete claim context: statement" in error for error in errors), errors)

    def test_delivery_requires_complete_measurement_card_and_wording_review(self) -> None:
        data = valid_manifest()
        data["visuals"][0]["measurement_card"]["denominator"] = ""
        data["visuals"][0]["wording_review"]["plain_language_passed"] = False
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("incomplete measurement card" in error for error in errors), errors)
        self.assertTrue(any("plain-language review" in error for error in errors), errors)

    def test_stakeholder_visual_requires_claim_lineage(self) -> None:
        data = valid_manifest()
        data["visuals"][0]["claim_ids"] = []
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("stakeholder visual requires claim_ids" in error for error in errors), errors)

    def test_active_delivery_artifact_requires_path_and_dependencies(self) -> None:
        data = valid_manifest()
        data["artifacts"][0]["path"] = ""
        data["artifacts"][0]["depends_on"] = []
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("incomplete active artifact" in error for error in errors), errors)

    def test_v1_migration_preserves_content_and_demotes_approvals(self) -> None:
        before = legacy_manifest()
        migrated = analysis_guard.migrate_v1_manifest(before)
        self.assertEqual("2.0", migrated["schema_version"])
        self.assertEqual(before["claims"][0]["statement"], migrated["claims"][0]["statement"])
        self.assertEqual("candidate", migrated["claims"][0]["status"])
        self.assertEqual("needs_validation", migrated["metrics"][0]["status"])
        self.assertEqual("ready_for_review", migrated["contract"]["status"])
        self.assertEqual("draft", migrated["visuals"][0]["intended_use"])
        self.assertEqual("stale", migrated["artifacts"][0]["status"])
        self.assertEqual("unknown", migrated["claims"][0]["claim_type"])
        self.assertEqual([], migrated["quality_checks"])
        self.assertEqual([], migrated["needs_discovery"]["permitted_claim_types"])
        self.assertNotIn("mode", migrated["needs_discovery"])
        self.assertEqual("not_started", migrated["analysis_brief"]["answer_status"])
        self.assertEqual([], analysis_guard.validate_manifest(migrated))

    def test_migrate_command_does_not_overwrite_source_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "analysis.json"
            source.write_text(json.dumps(legacy_manifest()), encoding="utf-8")
            original = source.read_text(encoding="utf-8")
            args = type("Args", (), {"manifest": source, "output": None, "write": False, "force": False})
            self.assertEqual(0, analysis_guard.command_migrate(args))
            self.assertEqual(original, source.read_text(encoding="utf-8"))
            migrated = json.loads((Path(temp) / "analysis.v2.json").read_text(encoding="utf-8"))
            self.assertEqual("2.0", migrated["schema_version"])

    def test_migrate_rejects_an_alias_of_the_source_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "analysis.json"
            source.write_text(json.dumps(legacy_manifest()), encoding="utf-8")
            original = source.read_bytes()
            aliased_output = source.parent / "." / source.name
            args = type(
                "Args",
                (),
                {"manifest": source, "output": aliased_output, "write": False, "force": False, "format": "json"},
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, analysis_guard.command_migrate(args))
            self.assertEqual(original, source.read_bytes())

    def test_quality_command_enforces_critical_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis.json"
            data = valid_manifest()
            data["quality_checks"][0].update({"status": "fail", "impact": "Material risk.", "required_action": "Resolve."})
            manifest.write_text(json.dumps(data), encoding="utf-8")
            args = type("Args", (), {"manifest": manifest, "fail_on_warning": False})
            self.assertEqual(1, analysis_guard.command_quality(args))

    def test_quality_command_allows_unpromoted_draft_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis.json"
            data = valid_manifest()
            data["status"] = "ready_for_execution"
            data["claims"][0].update({"status": "candidate", "evidence_posture": "needs_validation"})
            data["visuals"][0]["qa_status"] = "pending"
            data["artifacts"][0]["status"] = "draft"
            data["analysis_brief"].update({"answer_status": "not_started", "key_claim_ids": []})
            manifest.write_text(json.dumps(data), encoding="utf-8")
            args = type("Args", (), {"manifest": manifest, "fail_on_warning": False})
            self.assertEqual(0, analysis_guard.command_quality(args))

    def test_init_creates_minimal_visible_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            args = type("Args", (), {"output": Path(temp) / "run", "analysis_id": "example-run", "force": False})
            self.assertEqual(0, analysis_guard.command_init(args))
            self.assertTrue((Path(temp) / "run" / "analysis-manifest.json").exists())
            self.assertTrue((Path(temp) / "run" / "evidence").is_dir())
            self.assertTrue((Path(temp) / "run" / "analysis-brief.md").exists())

    def test_portability_scan_detects_secret_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "unsafe.txt"
            path.write_text(
                "api_key = '1234567890abcdefghijklmnop'\n"
                "source = 'C:\\\\Users\\\\Example\\\\private.csv'\n",
                encoding="utf-8",
            )
            findings = analysis_guard.scan_path(Path(temp))
            self.assertTrue(any("possible secret" in finding for finding in findings), findings)
            self.assertTrue(any("machine-specific absolute path" in finding for finding in findings), findings)

    def test_malformed_collections_report_errors_without_crashing(self) -> None:
        mutations = (
            ("quality_checks", None),
            ("claims", None),
            ("metrics", ["not-an-object"]),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                data = valid_manifest()
                data[field] = value
                errors = analysis_guard.validate_manifest(data)
                self.assertTrue(errors)

        data = valid_manifest()
        data["metrics"][0]["question_ids"] = None
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("M1.question_ids must be a list" in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis.json"
            malformed = valid_manifest()
            malformed["metrics"] = ["not-an-object"]
            malformed["claims"] = None
            manifest.write_text(json.dumps(malformed), encoding="utf-8")
            fingerprint_args = type("Args", (), {"manifest": manifest, "write": False, "format": "json"})
            stale_args = type(
                "Args", (), {"manifest": manifest, "write": False, "fail_on_stale": True, "format": "json"}
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, analysis_guard.command_fingerprint(fingerprint_args))
                self.assertEqual(1, analysis_guard.command_stale(stale_args))

    def test_load_json_accepts_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps(valid_manifest()), encoding="utf-8-sig")
            self.assertEqual("2.0", analysis_guard.load_json(path)["schema_version"])

    def test_atomic_json_write_cleans_temporary_file_after_serialization_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "manifest.json"
            with self.assertRaises(TypeError):
                analysis_guard.write_json_atomic(target, {"unsupported": {1, 2}})
            self.assertFalse(target.exists())
            self.assertEqual([], list(Path(temp).iterdir()))

    def test_question_parent_cycle_is_rejected(self) -> None:
        data = valid_manifest()
        second = copy.deepcopy(data["question_tree"]["questions"][0])
        second["question_id"] = "Q2"
        second["parent_id"] = "Q1"
        second["data_requirement_ids"] = []
        data["question_tree"]["questions"][0]["parent_id"] = "Q2"
        data["question_tree"]["questions"].append(second)
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("parent cycle" in error for error in errors), errors)

    def test_sparkline_named_chart_is_not_a_line_chart(self) -> None:
        data = valid_manifest()
        data["visuals"][0]["data_structure"]["ordered"] = False
        data["visuals"][0]["selected_chart"] = "sparkline_grid"
        errors = analysis_guard.validate_manifest(data)
        self.assertFalse(any("cannot use a line" in error for error in errors), errors)

    def test_metric_status_and_required_fingerprint_hash_are_enforced(self) -> None:
        data = valid_manifest()
        data["metrics"][0]["status"] = "Validated"
        data["metrics"][0].pop("fingerprint_hash")
        errors = analysis_guard.validate_manifest(data, stage="evidence")
        self.assertTrue(any("invalid status: Validated" in error for error in errors), errors)
        self.assertTrue(any("requires fingerprint_hash" in error for error in errors), errors)

    def test_instrumentation_and_experiment_routes_activate_practical_checks(self) -> None:
        for route, expected in (
            ("instrumentation_reliability", "instrumentation_semantics"),
            ("experiment", "experiment_srm"),
        ):
            with self.subTest(route=route):
                data = valid_manifest()
                data["analysis_blueprint"]["conditional_routes"].append(
                    {"route": route, "trigger": "Relevant data is present.", "rationale": "Validity depends on it.", "applied": True}
                )
                errors = analysis_guard.validate_manifest(data, stage="evidence")
                self.assertTrue(any(route in error and expected in error for error in errors), errors)

    def test_incomplete_analysis_brief_is_actionable_and_valid(self) -> None:
        data = valid_manifest()
        data["analysis_brief"].update(
            {
                "answer_status": "incomplete",
                "executive_answer": "The recorded pattern is real, but its full cause cannot yet be separated.",
                "unknowns": ["Whether consent loss explains the remaining telemetry gap."],
                "recommended_next_action": "Reconcile the event export with consent and release logs.",
            }
        )
        self.assertEqual([], analysis_guard.validate_manifest(data, stage="delivery"))
        brief = analysis_guard.build_analysis_brief(data)
        self.assertEqual("incomplete", brief["answer_status"])
        self.assertIn("consent", " ".join(brief["unknowns"]))
        rendered = analysis_guard.render_analysis_brief(brief)
        self.assertIn("## Executive answer", rendered)
        self.assertIn("## What remains unknown", rendered)

    def test_complete_analysis_brief_cannot_use_unapproved_or_absent_claims(self) -> None:
        data = valid_manifest()
        data["analysis_brief"]["key_claim_ids"] = []
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("complete analysis_brief requires key_claim_ids" in error for error in errors), errors)
        data = valid_manifest()
        data["claims"][0]["status"] = "validated"
        errors = analysis_guard.validate_manifest(data)
        self.assertTrue(any("analysis_brief uses non-approved claim" in error for error in errors), errors)

    def test_text_only_analysis_brief_can_be_a_complete_delivery(self) -> None:
        data = valid_manifest()
        data["visuals"] = []
        data["artifacts"][0].update(
            {
                "purpose": "decision-ready analysis brief",
                "path": "analysis-brief.md",
                "depends_on": ["M1", "C1"],
            }
        )
        self.assertEqual([], analysis_guard.validate_manifest(data, stage="delivery"))

    def test_delivery_requires_a_decision_ready_brief_or_passed_stakeholder_visual(self) -> None:
        data = valid_manifest()
        data.pop("analysis_brief")
        data["visuals"] = []
        data["artifacts"][0].update({"path": "output.bin", "depends_on": ["M1", "C1"]})
        errors = analysis_guard.validate_manifest(data, stage="delivery")
        self.assertTrue(any("decision-ready analysis brief or a stakeholder visual" in error for error in errors), errors)

    def test_passed_stakeholder_visual_can_be_the_delivery_without_a_brief(self) -> None:
        data = valid_manifest()
        data.pop("analysis_brief")
        self.assertEqual([], analysis_guard.validate_manifest(data, stage="delivery"))

    def test_brief_json_separates_generation_from_delivery_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis-manifest.json"
            data = valid_manifest()
            data["status"] = "draft"
            data["visuals"][0]["qa_status"] = "pending"
            data["artifacts"][0]["status"] = "draft"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            args = type("Args", (), {"manifest": manifest, "output": None, "format": "json"})
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, analysis_guard.command_brief(args))
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["generated"])
            self.assertEqual("complete", payload["answer_status"])
            self.assertFalse(payload["analysis_ready"])
            self.assertFalse(payload["delivery_ready"])
            self.assertNotIn("passed", payload)
            self.assertTrue(payload["delivery"]["validation_errors"])

    def test_brief_json_reports_analysis_and_delivery_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis-manifest.json"
            manifest.write_text(json.dumps(valid_manifest()), encoding="utf-8")
            args = type("Args", (), {"manifest": manifest, "output": None, "format": "json"})
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, analysis_guard.command_brief(args))
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["generated"])
            self.assertTrue(payload["analysis_ready"])
            self.assertTrue(payload["delivery_ready"])
            self.assertTrue(payload["delivery"]["passed"])

    def test_gate_and_json_output_pass_complete_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "analysis-manifest.json"
            manifest.write_text(json.dumps(valid_manifest()), encoding="utf-8")
            args = type(
                "Args",
                (),
                {
                    "manifest": manifest,
                    "stage": "delivery",
                    "scan_path": Path(temp),
                    "fail_on_warning": False,
                    "format": "json",
                },
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, analysis_guard.command_gate(args))
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["passed"])
            self.assertEqual([], payload["validation_errors"])


class RuntimeContractTest(unittest.TestCase):
    def test_all_six_problem_types_are_documented(self) -> None:
        text = (ROOT / "references" / "problem-type-playbooks.md").read_text(encoding="utf-8")
        headings = {
            "make_predictions": "## Make Predictions",
            "categorise_things": "## Categorise Things",
            "spot_unusual": "## Spot Something Unusual",
            "identify_themes": "## Identify Themes",
            "discover_connections": "## Discover Connections",
            "find_patterns": "## Find Patterns",
        }
        self.assertEqual(analysis_guard.PROBLEM_TYPES, set(headings))
        for heading in headings.values():
            self.assertIn(heading, text)

    def test_reasoning_kernel_precedes_blueprint_and_execution(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(skill.index("Interpret Before Structuring"), skill.index("Build The Analysis Blueprint"))
        self.assertLess(skill.index("Build The Analysis Blueprint"), skill.index("Execute Bounded Work"))
        reference = (ROOT / "references" / "needs-discovery-and-analysis-contract.md").read_text(encoding="utf-8")
        for term in ("Always-On Reasoning Kernel", "Analytical laddering", "Analysis Blueprint", "Question Roles"):
            self.assertIn(term, reference)

    def test_skill_uses_stable_route_ids_and_v2_question_roles(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for route in analysis_guard.CONDITIONAL_REASONING_ROUTES:
            self.assertIn(f"`{route}`", skill)
        self.assertIn("Never use legacy `core` or `supporting` roles", skill)
        self.assertIn("Record triggered routes with these exact IDs", skill)

    def test_skill_requires_the_useful_answer_in_conversation(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("directly in the conversation", skill)
        self.assertIn("files supplement rather than replace the answer", skill)
        self.assertIn("Do not end with only a file path or validation log", skill)

    def test_runtime_portability_scan_passes(self) -> None:
        runtime_paths = [ROOT / "SKILL.md", ROOT / "agents", ROOT / "references", ROOT / "assets", ROOT / "scripts"]
        for runtime_path in runtime_paths:
            findings = analysis_guard.scan_path(runtime_path)
            self.assertEqual([], findings, f"portability findings in {runtime_path}: {findings}")


if __name__ == "__main__":
    unittest.main()
