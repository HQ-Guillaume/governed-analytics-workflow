import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "forward_cases.json"
SPEC = importlib.util.spec_from_file_location(
    "analysis_guard", ROOT / "scripts" / "analysis_guard.py"
)
assert SPEC and SPEC.loader
analysis_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis_guard)
PROBLEM_TYPES = analysis_guard.PROBLEM_TYPES


class ForwardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_cases_are_generic_and_unique(self):
        ids = [case["case_id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 10)

        serialized = json.dumps(self.cases).lower()
        self.assertNotIn("http://", serialized)
        self.assertNotIn("https://", serialized)
        self.assertEqual([], analysis_guard.scan_path(FIXTURE))

    def test_all_problem_types_are_covered(self):
        covered = {case["primary_problem_type"] for case in self.cases}
        for case in self.cases:
            covered.update(case["secondary_problem_types"])
        self.assertEqual(PROBLEM_TYPES, covered)

    def test_material_confirmation_contracts_are_valid(self):
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertIsInstance(case["requires_framing_confirmation"], bool)
                self.assertIn(case["primary_problem_type"], PROBLEM_TYPES)

    def test_required_reasoning_is_present_in_references(self):
        reference_cache = {}
        for case in self.cases:
            relative_path = case["reference_file"]
            if relative_path not in reference_cache:
                reference_cache[relative_path] = (ROOT / relative_path).read_text(
                    encoding="utf-8"
                ).lower()

            with self.subTest(case=case["case_id"]):
                for phrase in case["required_phrases"]:
                    self.assertIn(phrase.lower(), reference_cache[relative_path])

    def test_ambiguous_and_causal_requests_require_material_confirmation(self):
        by_id = {case["case_id"]: case for case in self.cases}
        for case_id in (
            "ambiguous_stakeholder_request",
            "causal_request_without_design",
        ):
            case = by_id[case_id]
            self.assertTrue(case["requires_framing_confirmation"])


if __name__ == "__main__":
    unittest.main()
