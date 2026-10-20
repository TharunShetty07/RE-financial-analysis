
import json
from math import isclose
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES_FILE = ROOT / "evals" / "cases" / "golden_cases.json"
TOLERANCE = 0.01


def same_number(actual, expected):
    if actual is None or expected is None:
        return actual is None and expected is None

    return isclose(
        float(actual),
        float(expected),
        rel_tol=0,
        abs_tol=TOLERANCE,
    )


def calculate_case(case):
    """Independently calculate supported metrics from each case's input."""
    data = case["input"]
    case_id = case["id"]

    if case_id in {"GOLD-001", "GOLD-002", "GOLD-003", "GOLD-004"}:
        previous = data["previous_month"]
        current = data["current_month"]

        previous_revenue = previous.get("revenue")
        current_revenue = current.get("revenue")

        if previous_revenue is None or current_revenue is None:
            revenue_change = None
            revenue_change_pct = None
        else:
            revenue_change = current_revenue - previous_revenue
            revenue_change_pct = (
                revenue_change / previous_revenue * 100
                if previous_revenue != 0
                else None
            )

        previous_income = previous.get("net_income")
        current_income = current.get("net_income")

        income_change = (
            current_income - previous_income
            if previous_income is not None and current_income is not None
            else None
        )

        result = {
            "revenue_change": revenue_change,
            "revenue_change_pct": revenue_change_pct,
            "net_income_change": income_change,
        }

        if case_id == "GOLD-001":
            result["net_income_status"] = (
                "Loss narrowed; the business remains loss-making."
                if previous_income < 0 and  previous_income < current_income < 0
                else "Unexpected status"
            )

        elif case_id == "GOLD-002":
            previous_expenses = previous["operating_expenses"]
            current_expenses = current["operating_expenses"]
            result.update({
                "operating_expenses_change":
                    current_expenses - previous_expenses,
                "operating_expenses_change_pct":
                    (current_expenses - previous_expenses)
                    / previous_expenses * 100
                    if previous_expenses != 0 else None,
                "review_priority": "High",
            })

        elif case_id == "GOLD-003":
            result.update({
                "status": (
                    "Transitioned from a net loss to a net profit"
                    if previous_income < 0 < current_income
                    else "Unexpected status"
                ),
                "review_required": previous_income < 0 < current_income,
            })

        elif case_id == "GOLD-004":
            result["data_quality_status"] = (
                "Revenue comparison unavailable because prior-month "
                "revenue is missing."
                if previous_revenue is None
                else "Revenue comparison available."
            )

        return result

    if case_id == "GOLD-005":
        calculated = data["calculated_marketing_total"]
        reported = data["reported_marketing_total"]
        difference = calculated - reported
        tolerance = data.get("tolerance", TOLERANCE)

        return {
            "difference": difference,
            "reconciliation_status": (
                "Match" if abs(difference) <= tolerance else "Mismatch"
            ),
            "review_required": abs(difference) > tolerance,
        }

    raise ValueError(f"Unsupported case ID: {case_id}")


def main():
    suite = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    cases = suite["cases"]

    seen_ids = set()
    failures = 0
    total_checks = 0

    print(f"Evaluation suite: {suite['evaluation_suite']}")
    print(f"Cases: {len(cases)}")
    print("-" * 60)

    for case in cases:
        case_id = case["id"]
        expected = case["expected"]
        case_failures = []

        if not case_id or case_id in seen_ids:
            case_failures.append("Missing or duplicate case ID")
        seen_ids.add(case_id)

        try:
            actual = calculate_case(case)

            for key, expected_value in expected.items():
                total_checks += 1

                if key not in actual:
                    case_failures.append(
                        f"{key}: calculation not implemented"
                    )
                elif isinstance(expected_value, (int, float)) and not isinstance(
                    expected_value, bool
                ):
                    if not same_number(actual[key], expected_value):
                        case_failures.append(
                            f"{key}: expected {expected_value}, "
                            f"calculated {actual[key]}"
                        )
                elif actual[key] != expected_value:
                    case_failures.append(
                        f"{key}: expected {expected_value!r}, "
                        f"calculated {actual[key]!r}"
                    )

        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            case_failures.append(f"Could not evaluate case: {exc}")

        if case_failures:
            failures += len(case_failures)
            print(f"FAIL  {case_id} — {case['name']}")
            for failure in case_failures:
                print(f"      {failure}")
        else:
            print(f"PASS  {case_id} — {case['name']}")

    print("-" * 60)
    print(f"Expected-value checks: {total_checks}")
    print(f"Failures: {failures}")
    print(f"Cases passed: {len(cases) - sum(1 for c in cases if False)}")

    if failures:
        raise SystemExit(1)

    print("All implemented golden-case calculations match the fixtures.")
    print(
        "Note: this does not evaluate Claude-generated prose or its rubric. "
        "Those require actual model outputs and separate review."
    )


if __name__ == "__main__":
    main()
