
import copy
import json
import unittest
from pathlib import Path

from src.validation.golden_evaluator import calculate_case, same_number

ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "evals" / "cases" / "golden_cases.json"


class TestGoldenEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        suite = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in suite["cases"]}

    def test_all_five_fixtures_match_calculated_results(self):
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                actual = calculate_case(case)
                for key, expected in case["expected"].items():
                    self.assertIn(key, actual)
                    if isinstance(expected, (int, float)) and not isinstance(
                        expected, bool
                    ):
                        self.assertTrue(
                            same_number(actual[key], expected),
                            f"{case_id}: {key} expected {expected}, got {actual[key]}",
                        )
                    else:
                        self.assertEqual(actual[key], expected)

    def test_incorrect_expected_value_is_detectable(self):
        case = copy.deepcopy(self.cases["GOLD-001"])
        case["expected"]["revenue_change"] = 999999

        actual = calculate_case(case)

        self.assertFalse(
            same_number(actual["revenue_change"], case["expected"]["revenue_change"])
        )

    def test_missing_revenue_remains_unavailable(self):
        actual = calculate_case(self.cases["GOLD-004"])

        self.assertIsNone(actual["revenue_change"])
        self.assertIsNone(actual["revenue_change_pct"])
        self.assertEqual(actual["net_income_change"], 2000)

    def test_marketing_mismatch_is_flagged(self):
        actual = calculate_case(self.cases["GOLD-005"])

        self.assertEqual(actual["difference"], 500)
        self.assertEqual(actual["reconciliation_status"], "Mismatch")
        self.assertTrue(actual["review_required"])

    def test_loss_to_profit_transition_requires_review(self):
        actual = calculate_case(self.cases["GOLD-003"])

        self.assertEqual(actual["net_income_change"], 40000)
        self.assertTrue(actual["review_required"])


if __name__ == "__main__":
    unittest.main()
