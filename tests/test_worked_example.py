from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "worked_web_product_example.json"
REFERENCE = ROOT / "references" / "worked-web-product-example.md"
SPEC = importlib.util.spec_from_file_location("analysis_guard", ROOT / "scripts" / "analysis_guard.py")
assert SPEC and SPEC.loader
analysis_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis_guard)


class WorkedWebProductExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.reference = REFERENCE.read_text(encoding="utf-8")

    def test_reconciliation_is_complete_and_mutually_exclusive(self) -> None:
        sends = self.fixture["sends"]
        expected = self.fixture["expected_reconciliation"]
        self.assertEqual(expected["send_rows"], len(sends))
        self.assertEqual(expected["naive_matched"], sum(bool(item["naive_match"]) for item in sends))
        self.assertEqual(expected["naive_unmatched"], sum(not item["naive_match"] for item in sends))
        explained = [item for item in sends if not item["naive_match"] and item["final_reason"]]
        self.assertEqual(expected["explained_unmatched"], len(explained))
        self.assertEqual(expected["unexplained"], expected["naive_unmatched"] - len(explained))
        self.assertEqual(len(sends), len({item["attempt_id"] for item in sends}))

    def test_routes_and_quality_checks_are_runtime_contracts(self) -> None:
        self.assertTrue(set(self.fixture["required_routes"]) <= analysis_guard.CONDITIONAL_REASONING_ROUTES)
        required = set(self.fixture["required_quality_categories"])
        self.assertEqual(required, analysis_guard.ROUTE_REQUIRED_QUALITY["instrumentation_reliability"])

    def test_reference_contains_every_cause_and_analysis_brief_section(self) -> None:
        for item in self.fixture["sends"]:
            if item["final_reason"] != "valid_match":
                readable = item["final_reason"].replace("_", " ")
                with self.subTest(reason=readable):
                    self.assertIn(readable.split()[0], self.reference.lower())
        for heading in self.fixture["required_brief_sections"]:
            self.assertIn(heading, analysis_guard.render_analysis_brief({}))
        self.assertEqual([], analysis_guard.scan_path(REFERENCE))


if __name__ == "__main__":
    unittest.main()
