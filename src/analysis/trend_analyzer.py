
from __future__ import annotations

from typing import Any


def _get_total(
    data: dict[str, Any],
    total_name: str,
    month: str,
) -> float | None:
    """Get a reported financial total for a given month."""
    values = (
        data.get("reported_totals", {})
        .get("income_statement", {})
        .get(total_name, {})
    )
    value = values.get(month)

    return float(value) if value is not None else None


def _percentage_change(
    current: float | None,
    previous: float | None,
) -> float | None:
    """Calculate percentage change safely."""
    if current is None or previous is None or previous == 0:
        return None

    return ((current - previous) / abs(previous)) * 100


def _margin(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    """Calculate a margin percentage safely."""
    if numerator is None or denominator is None or denominator == 0:
        return None

    return (numerator / denominator) * 100


def analyze_monthly_trends(
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate monthly financial trends and expense categories.

    Reported totals are used for headline metrics to avoid double-counting
    account details and their subtotals.
    """
    months = data.get("months", [])

    if not months:
        raise ValueError("No reporting months were provided.")

    monthly_results: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. Monthly financial metrics
    # ---------------------------------------------------------
    for index, month in enumerate(months):
        revenue = _get_total(data, "Total Income", month)
        cogs = _get_total(data, "Total Cost of Goods Sold", month)
        gross_profit = _get_total(data, "Gross Profit", month)
        operating_expenses = _get_total(
            data, "Total Operating Expenses", month
        )
        operating_income = _get_total(data, "Operating Income", month)
        net_income = _get_total(data, "Net Income", month)

        previous_month = months[index - 1] if index > 0 else None

        previous_revenue = (
            _get_total(data, "Total Income", previous_month)
            if previous_month
            else None
        )

        previous_net_income = (
            _get_total(data, "Net Income", previous_month)
            if previous_month
            else None
        )

        monthly_results.append({
            "month": month,
            "revenue": revenue,
            "cost_of_goods_sold": cogs,
            "gross_profit": gross_profit,
            "gross_margin_pct": _margin(gross_profit, revenue),
            "operating_expenses": operating_expenses,
            "operating_income": operating_income,
            "net_income": net_income,
            "net_profit_margin_pct": _margin(net_income, revenue),
            "revenue_mom_change": (
                revenue - previous_revenue
                if revenue is not None and previous_revenue is not None
                else None
            ),
            "revenue_mom_change_pct": _percentage_change(
                revenue, previous_revenue
            ),
            "net_income_mom_change": (
                net_income - previous_net_income
                if net_income is not None
                and previous_net_income is not None
                else None
            ),
        })

    # ---------------------------------------------------------
    # 2. Trailing-12-month metrics
    # ---------------------------------------------------------
    for index, result in enumerate(monthly_results):
        if index < 11:
            result["trailing_12_month_revenue"] = None
            result["trailing_12_month_net_income"] = None
            continue

        window = monthly_results[index - 11:index + 1]

        revenues = [item["revenue"] for item in window]
        net_incomes = [item["net_income"] for item in window]

        result["trailing_12_month_revenue"] = (
            sum(revenues)
            if all(value is not None for value in revenues)
            else None
        )

        result["trailing_12_month_net_income"] = (
            sum(net_incomes)
            if all(value is not None for value in net_incomes)
            else None
        )

    # ---------------------------------------------------------
    # 3. Expense category mapping
    # ---------------------------------------------------------
    income_accounts = data.get("income_statement", {})
    income_totals = (
        data.get("reported_totals", {}).get("income_statement", {})
    )

    expense_categories = {
        "Operating Expenses - Direct": [
            "Accounting & Tax",
            "Advisory Services",
            "Bad Debts",
            "Bank Service Charges",
            "Bonus",
            "Consulting",
            "Contribution to Charities",
            "Depreciation",
            "Development - Contractor",
            "Development Payroll",
            "Employee Training expenses",
            "Federal & State Taxes",
            "General Expenses",
            "Health Insurance",
            "Insurance",
            "Interest Expense",
            "Interest Income",
            "Legal Expenses",
        ],
        "S & M Payroll": [
            "Marketing - Payroll",
            "Marketing - Payroll benefits",
            "Marketing - Payroll Taxes",
            "Marketing - Workers Comp Insurance",
            "Partnerships - Payroll",
            "Partnerships - Payroll benefits",
            "Partnerships - Payroll Taxes",
            "Sales - Payroll",
            "Sales - Payroll benefits",
            "Sales - Payroll Taxes",
            "Sales - Workers Comp Insurance",
        ],

        "Marketing": [
            "Marketing/Advertising",
            "Marketing/Advertising: Ad Spend",
            "Marketing/Advertising: Print & Digital",
            "Marketing/Advertising: 3rd Party Content Syndication",
            "Events & Conferences",
            "Marketing/Advertising: Content",
            "Marketing/Advertising: Membership Dues/Subscriptions",
            "Marketing/Advertising: Miscellaneous",
            "Marketing/Advertising: Website",
            "Marketing/Advertising: Partner Marketing",
        ],

        "Other Operating Expenses": [
            "Meals & Entertainment",
            "Merchant fees",
            "Office Expenses",
            "Operating Payroll",
            "Operations - Payroll benefits",
            "Operations - Workers Comp Insurance",
            "Operations Payroll Taxes",
            "Payroll Service Fee",
            "Postage & Delivery",
            "Printing & Stationery",
            "Product - Payroll benefits",
            "Product - Workers Comp Insurance",
            "Product Payroll Taxes",
            "Professional Fees",
            "Recruiting Expense",
            "Rent",
            "Sales & Marketing - Contractor",
            "Sales & Marketing - Workers Comp Insurance",
            "Sales & Marketing Payroll",
            "Sales & Marketing Payroll Taxes",
            "Sales and Marketing - Payroll benefits",
            "Severance",
            "Software & SaaS",
            "Telephone & Internet",
            "Travel",
            "Partnerships Commission",
            "Workers Compensation Insurance",
            "Stock-Based Compensation Expense",
            "Sales & Marketing - Travel, Meals & Entertainment",
            "Income Tax Benefit",
            "AI Token Cost",
        ],
    }

    category_trends: dict[str, dict[str, Any]] = {}

    for category, account_names in expense_categories.items():
        category_trends[category] = {}

        for month in months:
            values = [
                income_accounts[name].get(month)
                for name in account_names
                if name in income_accounts
                and income_accounts[name].get(month) is not None
            ]

            category_trends[category][month] = (
                sum(values) if values else None
            )

    # Retain source-reported subtotals separately.
    # Do not add these subtotal values to their detail accounts.
    category_trends["Reported S & M Payroll Subtotal"] = (
        income_totals.get("Total S & M Payroll", {})
    )

    category_trends["Reported Marketing Subtotal"] = (
        income_totals.get("Total Marketing", {})
    )

    # ---------------------------------------------------------
    # 4. Reconcile mapped categories with reported subtotals
    # ---------------------------------------------------------
    category_reconciliation: list[dict[str, Any]] = []

    reconciliation_pairs = [
        (
            "S & M Payroll",
            "Reported S & M Payroll Subtotal",
        ),
        (
            "Marketing",
            "Reported Marketing Subtotal",
        ),
    ]

    for month in months:
        for calculated_name, reported_name in reconciliation_pairs:
            calculated = category_trends[calculated_name].get(month)
            reported = category_trends[reported_name].get(month)

            if calculated is None or reported is None:
                difference = None
                matches = None
            else:
                difference = calculated - reported
                matches = abs(difference) <= 0.01

            category_reconciliation.append({
                "month": month,
                "category": calculated_name,
                "calculated_total": calculated,
                "reported_total": reported,
                "difference": difference,
                "matches": matches,
            })

    # ---------------------------------------------------------
    # 5. Human-review flags
    # ---------------------------------------------------------
    review_flags: list[dict[str, str]] = []

    for index, result in enumerate(monthly_results):
        if index == 0:
            continue

        change_pct = result["revenue_mom_change_pct"]

        if change_pct is not None and abs(change_pct) >= 15:
            direction = "increased" if change_pct > 0 else "decreased"

            review_flags.append({
                "month": result["month"],
                "metric": "Revenue",
                "message": (
                    f"Revenue {direction} by {abs(change_pct):.2f}% "
                    "month over month; review the underlying drivers."
                ),
            })

        net_income = result["net_income"]
        previous_net_income = monthly_results[index - 1]["net_income"]

        if (
            net_income is not None
            and net_income > 0
            and previous_net_income is not None
            and previous_net_income <= 0
        ):
            review_flags.append({
                "month": result["month"],
                "metric": "Net Income",
                "message": (
                    "Net income moved from zero or a loss to a profit; "
                    "verify the underlying transactions."
                ),
            })

    # ---------------------------------------------------------
    # 6. Return results
    # ---------------------------------------------------------
    return {
        "months_analyzed": len(months),
        "period_start": months[0],
        "period_end": months[-1],
        "monthly_results": monthly_results,
        "category_trends": category_trends,
        "category_reconciliation": category_reconciliation,
        "review_flags": review_flags,
    }
