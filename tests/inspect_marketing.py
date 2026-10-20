
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis.workbook_parser import load_workbook_data

data = load_workbook_data(ROOT / "data" / "financial_statements.xlsx")

accounts = data["income_statement"]
reported = data["reported_totals"]["income_statement"]["Total Marketing"]

for month in ["2025-01", "2025-02", "2026-06"]:
    print(f"\n--- {month} ---")
    print(f"Reported marketing subtotal: {reported[month]}")

    for name, values in accounts.items():
        value = values.get(month)
        if value is not None and value != 0:
            print(f"{name}: {value}")
