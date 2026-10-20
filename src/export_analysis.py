
import json
from pathlib import Path

from src.analysis.workbook_parser import load_workbook_data
from src.analysis.trend_analyzer import analyze_monthly_trends


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "financial_statements.xlsx"
OUTPUT = ROOT / "reports" / "monthly_analysis.json"


def main():
    source_data = load_workbook_data(WORKBOOK)
    analysis = analyze_monthly_trends(source_data)

    export = {
        "reporting_period": {
            "start": analysis["period_start"],
            "end": analysis["period_end"],
            "months_analyzed": analysis["months_analyzed"],
        },
        "monthly_results": analysis["monthly_results"],
        "expense_category_trends": analysis["category_trends"],
        "category_reconciliation": analysis["category_reconciliation"],
        "review_flags": analysis["review_flags"],
        "data_quality": {
            "warning_count": len(source_data["warnings"]),
            "warnings": source_data["warnings"],
        },
        "methodology": {
            "source_file": source_data["source_file"],
            "currency": "Not specified; amounts remain in source workbook units.",
            "trailing_12_months": (
                "Calculated only when 12 consecutive months of data are available."
            ),
            "human_review_required": True,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(export, file, indent=2, ensure_ascii=False, allow_nan=False)

    print(f"Export created: {OUTPUT}")
    print(f"Reporting period: {analysis['period_start']} to {analysis['period_end']}")
    print(f"Months analyzed: {analysis['months_analyzed']}")
    print(f"Review flags: {len(analysis['review_flags'])}")
    print(f"Data-quality warnings: {len(source_data['warnings'])}")


if __name__ == "__main__":
    main()
