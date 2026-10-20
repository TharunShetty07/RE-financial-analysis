
import unittest
from pathlib import Path

from src.analysis.workbook_parser import load_workbook_data
from src.analysis.trend_analyzer import analyze_monthly_trends


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = PROJECT_ROOT / "data" / "financial_statements.xlsx"


class TestTrendAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source_data = load_workbook_data(WORKBOOK_PATH)
        cls.analysis = analyze_monthly_trends(cls.source_data)
        cls.months = cls.source_data["months"]

    def test_all_18_months_are_analyzed(self):
        self.assertEqual(self.analysis["months_analyzed"], 18)
        self.assertEqual(len(self.analysis["monthly_results"]), 18)
        self.assertEqual(self.analysis["period_start"], "2025-01")
        self.assertEqual(self.analysis["period_end"], "2026-06")

    def test_headline_metrics_match_source_totals(self):
        """Computed report metrics must match the workbook's reported totals."""
        metric_mapping = {
            "revenue": "Total Income",
            "cost_of_goods_sold": "Total Cost of Goods Sold",
            "gross_profit": "Gross Profit",
            "operating_expenses": "Total Operating Expenses",
            "operating_income": "Operating Income",
            "net_income": "Net Income",
        }

        reported_totals = self.source_data["reported_totals"]["income_statement"]

        for record in self.analysis["monthly_results"]:
            month = record["month"]

            for metric, total_name in metric_mapping.items():
                with self.subTest(month=month, metric=metric):
                    expected = reported_totals[total_name][month]
                    actual = record[metric]

                    self.assertIsNotNone(expected)
                    self.assertIsNotNone(actual)
                    self.assertAlmostEqual(
                        actual, expected, places=2,
                        msg=f"{metric} differs from the source for {month}"
                    )

    def test_trailing_12_month_windows(self):
        """TTM values must be absent before 12 months of data exist."""
        records = self.analysis["monthly_results"]

        for record in records[:11]:
            with self.subTest(month=record["month"]):
                self.assertIsNone(record["trailing_12_month_revenue"])
                self.assertIsNone(record["trailing_12_month_net_income"])

        self.assertEqual(len(records[11:]), 7)

        for index in range(11, len(records)):
            record = records[index]
            window = records[index - 11:index + 1]

            expected_revenue = sum(item["revenue"] for item in window)
            expected_net_income = sum(item["net_income"] for item in window)

            with self.subTest(month=record["month"], metric="TTM revenue"):
                self.assertAlmostEqual(
                    record["trailing_12_month_revenue"],
                    expected_revenue,
                    places=2,
                )

            with self.subTest(month=record["month"], metric="TTM net income"):
                self.assertAlmostEqual(
                    record["trailing_12_month_net_income"],
                    expected_net_income,
                    places=2,
                )

    def test_payroll_and_marketing_subtotals_reconcile(self):
        """Mapped payroll and marketing details must match reported subtotals."""
        checks = self.analysis["category_reconciliation"]

        self.assertEqual(len(checks), 36)  # 18 months × 2 categories

        for check in checks:
            with self.subTest(
                month=check["month"],
                category=check["category"],
            ):
                self.assertTrue(
                    check["matches"],
                    msg=(
                        f"{check['category']} mismatch for {check['month']}: "
                        f"calculated={check['calculated_total']}, "
                        f"reported={check['reported_total']}, "
                        f"difference={check['difference']}"
                    ),
                )

    def test_expense_categories_cover_reported_operating_expenses(self):
        """The four detail groups must reconcile to total operating expenses."""
        categories = [
            "Operating Expenses - Direct",
            "S & M Payroll",
            "Marketing",
            "Other Operating Expenses",
        ]

        category_trends = self.analysis["category_trends"]
        reported_totals = self.source_data["reported_totals"]["income_statement"]
        total_operating_expenses = reported_totals["Total Operating Expenses"]

        for month in self.months:
            category_values = [
                category_trends[category].get(month)
                for category in categories
            ]

            with self.subTest(month=month):
                self.assertTrue(
                    all(value is not None for value in category_values),
                    msg=f"Missing category value for {month}",
                )

                calculated_total = sum(category_values)
                reported_total = total_operating_expenses[month]

                self.assertIsNotNone(reported_total)
                self.assertAlmostEqual(
                    calculated_total,
                    reported_total,
                    places=2,
                    msg=(
                        f"Expense categories do not reconcile for {month}: "
                        f"calculated={calculated_total}, "
                        f"reported={reported_total}"
                    ),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
