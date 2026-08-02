from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "reasoning_benchmarks.json"
HISTORICAL_RESULTS_FIXTURE = ROOT / "tests" / "fixtures" / "forward_results_v2.json"
RESULTS_FIXTURE = ROOT / "tests" / "fixtures" / "forward_results_v2_1_1.json"
SPEC = importlib.util.spec_from_file_location("analysis_guard", ROOT / "scripts" / "analysis_guard.py")
assert SPEC and SPEC.loader
analysis_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis_guard)


class ReasoningBenchmarkContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = cls.benchmark["cases"]

    def test_rubric_matches_release_acceptance_dimensions(self) -> None:
        dimensions = self.benchmark["rubric"]["dimensions"]
        self.assertEqual(20, sum(dimensions.values()))
        self.assertEqual(16, self.benchmark["rubric"]["pass_score"])
        self.assertEqual(
            {
                "real_need_identification",
                "alternative_framing",
                "necessary_context",
                "irrelevant_analysis_excluded",
                "data_plan_completeness",
                "definition_and_method_correctness",
                "evidence_limits_and_claim_discipline",
                "presentation_clarity",
            },
            set(dimensions),
        )
        self.assertGreaterEqual(len(self.benchmark["rubric"]["critical_failures"]), 5)

    def test_cases_are_blind_generic_and_unique(self) -> None:
        ids = [case["case_id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 12)
        serialized = json.dumps(self.benchmark).lower()
        self.assertNotIn("http://", serialized)
        self.assertNotIn("https://", serialized)
        self.assertNotIn("expected_response", serialized)
        self.assertNotIn("gold_answer", serialized)
        self.assertEqual([], analysis_guard.scan_path(FIXTURE))

    def test_each_problem_type_has_two_blind_cases(self) -> None:
        counts = Counter(case["primary_problem_type"] for case in self.cases)
        self.assertEqual(analysis_guard.PROBLEM_TYPES, set(counts))
        for problem_type in analysis_guard.PROBLEM_TYPES:
            self.assertGreaterEqual(counts[problem_type], 2)

    def test_cases_define_operational_expectations_without_prescribing_an_answer(self) -> None:
        required_fields = {
            "case_id",
            "raw_request",
            "primary_problem_type",
            "secondary_problem_types",
            "required_routes",
            "required_reasoning",
            "necessary_context",
            "excluded_analysis",
            "data_plan_requirements",
            "claim_ceiling",
            "material_clarification",
        }
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(required_fields, set(case))
                self.assertGreaterEqual(len(case["raw_request"]), 80)
                self.assertIn(case["primary_problem_type"], analysis_guard.PROBLEM_TYPES)
                self.assertTrue(set(case["secondary_problem_types"]) <= analysis_guard.PROBLEM_TYPES)
                self.assertTrue(set(case["required_routes"]) <= analysis_guard.CONDITIONAL_REASONING_ROUTES)
                self.assertGreaterEqual(len(case["required_reasoning"]), 3)
                self.assertGreaterEqual(len(case["data_plan_requirements"]), 3)
                self.assertTrue(case["claim_ceiling"].strip())

    def test_all_conditional_route_families_are_exercised(self) -> None:
        covered = {route for case in self.cases for route in case["required_routes"]}
        self.assertEqual(analysis_guard.CONDITIONAL_REASONING_ROUTES, covered)

    def test_blind_forward_results_pass_release_acceptance(self) -> None:
        results = json.loads(RESULTS_FIXTURE.read_text(encoding="utf-8"))
        rubric = self.benchmark["rubric"]
        benchmark_cases = {case["case_id"]: case for case in self.cases}
        release = json.loads((ROOT / "assets" / "release.json").read_text(encoding="utf-8"))
        self.assertEqual(release["version"], results["skill_version"])
        self.assertIn("Current v2.1.1", results["result_scope"])
        self.assertIn("did not receive benchmark expectations", results["blind_input_contract"])
        self.assertEqual(len(self.cases), len(results["cases"]))
        self.assertEqual(set(benchmark_cases), {case["case_id"] for case in results["cases"]})
        self.assertEqual(analysis_guard.PROBLEM_TYPES, {case["primary_problem_type"] for case in results["cases"]})
        for result in results["cases"]:
            with self.subTest(case=result["case_id"]):
                self.assertIn(result["case_id"], benchmark_cases)
                self.assertTrue(result["response"].strip())
                self.assertEqual(set(rubric["dimensions"]), set(result["scores"]))
                self.assertEqual(sum(result["scores"].values()), result["total"])
                self.assertGreaterEqual(result["total"], rubric["pass_score"])
                self.assertFalse(result["critical_failure"])
                self.assertEqual("pass", result["result"])
        totals = [result["total"] for result in results["cases"]]
        self.assertEqual(min(totals), results["summary"]["minimum_score"])
        self.assertEqual(max(totals), results["summary"]["maximum_score"])
        self.assertEqual(0, results["summary"]["critical_failures"])
        self.assertTrue(results["summary"]["passed"])
        self.assertEqual([], analysis_guard.scan_path(RESULTS_FIXTURE))

    def test_historical_forward_baseline_remains_clearly_labelled(self) -> None:
        results = json.loads(HISTORICAL_RESULTS_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual("2.0.0", results["skill_version"])
        self.assertIn("Historical v2.0.0", results["result_scope"])
        self.assertIn("not represented as a v2.1.0 rerun", results["result_scope"])
        self.assertEqual(6, len(results["cases"]))


if __name__ == "__main__":
    unittest.main()
