# Trend Analyzer — Regression Test Results

## Objective
Validate the monthly financial trend analyzer against the supplied fictional financial statements workbook.

## Test Execution
Command: `python -m unittest tests.test_trend_analyzer -v`

Result: **5 tests passed, 0 failures.**

## Coverage
1. **Reporting period:** Confirms all 18 months are analyzed, from January 2025 through June 2026.
2. **Headline metrics:** Validates revenue, cost of goods sold, gross profit, operating expenses, operating income, and net income against reported workbook totals.
3. **Trailing-12-month calculations:** Verifies rolling 12-month revenue and net income calculations, including the requirement for 12 months of available data.
4. **Subtotal reconciliation:** Checks calculated sales and marketing payroll and marketing subtotals against the workbook's reported subtotals across all 18 months.
5. **Expense-category reconciliation:** Confirms the four mapped expense categories sum to reported total operating expenses for every reporting month.

## Defect Found and Resolved
Initial tests identified a missing `Marketing/Advertising` account in the marketing category mapping. The omission caused subtotal discrepancies in January and February 2025 and corresponding differences in total operating expenses. The mapping was corrected, and the full test suite subsequently passed.

## Regression Strategy
Run the test suite after any change to workbook parsing, account mapping, financial calculations, or reporting logic. Investigate failures against the source workbook rather than changing expected results simply to obtain a passing test.

## Scope and Limitations
These tests validate calculations and reconciliation against the supplied workbook. They do not independently establish the accounting correctness of the source data or validate a live QuickBooks connection.

## QuickBooks Online Sandbox Connection

**Status:** Successfully verified on 21 October 2026.

- **Integration:** QuickBooks Online API using OAuth 2.0
- **Environment:** Intuit developer sandbox
- **Verification:** Successfully retrieved company information from the sandbox API.
- **Company:** Sandbox Company US d20c
- **Evidence:** `docs/qbo-sandbox-connection.png`
- **Credential handling:** Client credentials are loaded from the local `.env` file and must not be committed to version control. OAuth tokens and client secrets are not displayed in the successful response.
- **Scope:** Sandbox connection verification only. Live production access and full financial-data synchronization have not yet been verified.

**Security note:** The local Flask server is for development and demonstration only. A production deployment requires a hardened server, secure token storage, HTTPS, and appropriate access controls.