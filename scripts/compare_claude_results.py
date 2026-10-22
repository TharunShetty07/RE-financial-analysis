
import json
import math
from pathlib import Path

# Load Claude's analysis and the local analysis
claude_path = Path("reports/trend_results.json")
local_path = Path("reports/monthly_analysis.json")

if not claude_path.exists():
    raise FileNotFoundError(f"Claude results not found: {claude_path}")

if not local_path.exists():
    raise FileNotFoundError(f"Local results not found: {local_path}")

claude = json.loads(claude_path.read_text(encoding="utf-8"))
local = json.loads(local_path.read_text(encoding="utf-8"))

# Index both reports by month
c_rows = {row["month"]: row for row in claude["monthly"]}
l_rows = {row["month"]: row for row in local["monthly_results"]}

# Claude field -> local analysis field
mapping = {
    "revenue": "revenue",
    "cogs": "cost_of_goods_sold",
    "gross_profit": "gross_profit",
    "gross_margin_pct": "gross_margin_pct",
    "opex": "operating_expenses",
    "operating_income": "operating_income",
    "net_income": "net_income",
    "net_margin_pct": "net_profit_margin_pct",
    "rev_mom_abs": "revenue_mom_change",
    "rev_mom_pct": "revenue_mom_change_pct",
    "ni_mom_abs": "net_income_mom_change",
    "ttm_revenue": "trailing_12_month_revenue",
    "ttm_net_income": "trailing_12_month_net_income",
}

months = sorted(set(c_rows) | set(l_rows))
failures = []
comparisons = 0

for month in months:
    if month not in c_rows or month not in l_rows:
        failures.append(f"{month}: month missing from one report")
        continue

    for claude_key, local_key in mapping.items():
        a = c_rows[month].get(claude_key)
        b = l_rows[month].get(local_key)

        # Both missing means the metric is unavailable for that month.
        if a is None and b is None:
            continue

        comparisons += 1

        if a is None or b is None:
            failures.append(
                f"{month} {claude_key}: Claude={a}, local={b}"
            )
        elif not math.isclose(
            float(a),
            float(b),
            rel_tol=1e-9,
            abs_tol=0.01,
        ):
            failures.append(
                f"{month} {claude_key}: Claude={a}, local={b}"
            )

print("=" * 55)
print("CLAUDE VS LOCAL FINANCIAL ANALYSIS")
print("=" * 55)
print(f"Claude months: {len(c_rows)}")
print(f"Local months: {len(l_rows)}")
print(f"Months compared: {len(months)}")
print(f"Metrics defined per month: {len(mapping)}")
print(f"Actual value comparisons: {comparisons}")
print(f"Mismatches: {len(failures)}")

if failures:
    print("\nFAIL: Differences found")
    for failure in failures:
        print(f"MISMATCH: {failure}")
    raise SystemExit(1)

if len(c_rows) != 18 or len(l_rows) != 18:
    print("\nFAIL: Expected exactly 18 months in both reports.")
    raise SystemExit(1)

print("\nPASS: All comparable headline metrics match within 0.01.")
print("PASS: Both reports contain all 18 months.")
