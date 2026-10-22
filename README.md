# RE Financial Services — Financial Analysis & AI Solutions Builder

## Project Overview

This project implements a reusable monthly financial trend analysis workflow using a supplied Excel workbook containing 18 months of fictional financial statements. It includes workbook parsing, financial metric calculations, month-over-month comparisons, trailing-12-month analysis, data-quality checks, a reusable Claude skill, and golden evaluation cases.

The project also includes a custom Model Context Protocol (MCP) server that connects Claude Desktop to a QuickBooks Online (QBO) developer sandbox using OAuth 2.0 authentication.

**Current status:** The local financial analysis pipeline and golden-case evaluation suite have been implemented and tested. The QBO sandbox connection has been verified through the custom MCP server. A workbook-based Claude analysis has been compared against the local analysis, with zero mismatches across 209 actual value comparisons. An in-memory prototype demonstrates client-level data access checks for ten fictional clients. Workbook analysis, QuickBooks integration, and client isolation remain separate components. Automated workbook-to-QBO data loading, a combined end-to-end QBO-to-Claude workflow, and production multi-client hosting have not been implemented.

## Key Features

- **Workbook parsing:** Reads the Income Statement and Balance Sheet from the supplied Excel workbook.
- **Monthly financial analysis:** Calculates revenue, cost of goods sold (COGS), gross profit, gross margin, operating expenses, operating income, net income, and net margin.
- **Trend analysis:** Calculates month-over-month changes and trailing-12-month metrics where sufficient data is available.
- **Expense analysis:** Groups expenses into categories and checks category reconciliation.
- **Data-quality checks:** Preserves source values and flags items requiring review instead of silently modifying questionable data.
- **Reusable Claude skill:** Defines expected inputs, analysis procedures, outputs, validation rules, and human-review requirements.
- **Golden evaluations:** Includes five evaluation cases covering revenue trends, expense changes, profitability transitions, missing comparison data, and reconciliation issues.
- **Claude output comparison:** Compares exported Claude analysis results with the local deterministic analysis for compatible headline metrics.
- **Client-isolation prototype:** Demonstrates separate in-memory datasets, client-level access checks, duplicate-registration protection, and defensive copies.
- **QuickBooks sandbox integration:** Provides a custom MCP server with tools to verify the sandbox connection and retrieve the chart of accounts.
- **OAuth token refresh:** Implements access-token refresh and persists updated token credentials.
- **Security-conscious configuration:** Keeps credentials and token files outside version control and restricts the MCP server to the sandbox environment.

## Project Structure

```text
RE Financial/
├── data/
│   └── financial_statements.xlsx
├── docs/
│   ├── architecture.md
│   └── testing.md
├── evals/
│   └── cases/
│       └── golden_cases.json
├── reports/                         # Generated local reports; Git-ignored
│   ├── monthly_analysis.json
│   └── trend_results.json            # Claude analysis output
├── scripts/
│   └── compare_claude_results.py
├── skills/
│   └── monthly-trend-analysis/
│       └── SKILL.md
├── src/
│   ├── analysis/
│   │   ├── workbook_parser.py
│   │   └── trend_analyzer.py
│   ├── validation/
│   │   └── golden_evaluator.py
│   ├── client_isolation.py
│   ├── export_analysis.py
│   ├── qbo_oauth.py
│   └── qbo_mcp_server.py
├── tests/
│   ├── test_client_isolation.py
│   ├── test_golden_evaluator.py
│   ├── test_trend_analyzer.py
│   └── inspect_marketing.py
├── .gitignore
└── README.md
```

Generated reports, local OAuth token files, environment files, and other sensitive local artifacts must remain excluded from version control. The exact contents of generated reports may vary.

## Requirements

- Python 3.11 or a compatible version.
- pip.
- QuickBooks Online developer sandbox credentials for the OAuth demonstration.
- The supplied fictional financial statements workbook.
- Claude Desktop for interacting with the custom MCP server.

## Setup

Open PowerShell in the project root directory.

Install the required dependencies:

```powershell
python -m pip install openpyxl flask intuit-oauth requests python-dotenv "mcp<2"
```

Ensure the supplied workbook is available at:

```text
data/financial_statements.xlsx
```

### Environment Configuration

Create a local `.env` file in the project root containing the QuickBooks developer application credentials and configuration expected by the implementation.

The configuration uses these environment variable names:

```text
QBO_CLIENT_ID
QBO_CLIENT_SECRET
QBO_REDIRECT_URI
QBO_ENVIRONMENT
FLASK_SECRET_KEY
```

Set `QBO_ENVIRONMENT` to `sandbox`. Configure `QBO_REDIRECT_URI` to match the redirect URI registered in the QuickBooks developer application. For the current local setup, the redirect URI is:

```text
http://localhost:8000/callback
```

Use a securely generated, stable `FLASK_SECRET_KEY` for the local OAuth session. Do not share its value.

**Security requirements:**

- Never commit `.env` or other credential files.
- Never hardcode client secrets, access tokens, or refresh tokens.
- Keep `token.json` local and excluded from Git.
- Use sandbox credentials and fictional data only.
- Do not share authorization codes, tokens, or secrets in screenshots or logs.
- Do not switch the integration to a live QuickBooks company without a separate security review and explicit authorization.

## Running the Financial Analysis

From the project root, run:

```powershell
python .\src\export_analysis.py
```

The analysis export is written to:

```text
reports/monthly_analysis.json
```

The report is generated locally, and the `reports/` directory is ignored by Git.

## Running the Tests

Run the complete automated test suite:

```powershell
python -m unittest discover -s tests -v
```

The latest complete test run passed **17 tests with zero failures**.

Run the trend-analysis unit tests:

```powershell
python -m unittest tests.test_trend_analyzer -v
```

Run the golden-evaluation unit tests:

```powershell
python -m unittest tests.test_golden_evaluator -v
```

Run the client-isolation prototype tests:

```powershell
python -m unittest tests.test_client_isolation -v
```

The tests cover financial calculations, trend analysis, missing values, expense reconciliation, golden-case evaluation, and client-isolation behavior.

### Golden Evaluation Suite

Run the golden-case evaluator:

```powershell
python .\src\validation\golden_evaluator.py
```

The latest evaluation completed with:

- **Cases passed:** 5 of 5.
- **Expected-value checks:** 22.
- **Failures:** 0.

The golden cases cover:

1. Revenue increase.
2. Revenue decline with higher expenses.
3. Loss-to-profit transition.
4. Missing comparison data.
5. Expense subtotal mismatch.

The evaluator checks structured calculated values against expected fixtures. It does **not** automatically grade Claude-generated narrative quality. Commentary, unsupported claims, explanations, and human-review recommendations require separate evaluation against the rubric and actual model outputs.

## Claude Skill

The reusable skill is located at:

```text
skills/monthly-trend-analysis/SKILL.md
```

It defines the analysis procedure, expected outputs, calculation conventions, validation requirements, and human-review flags.

A workbook-based analysis was executed in Claude using the supplied fictional financial statements. The exported results were saved locally as:

```text
reports/trend_results.json
```

The local deterministic analysis is exported to:

```text
reports/monthly_analysis.json
```

### Claude and Local Analysis Comparison

The comparison script is located at:

```text
scripts/compare_claude_results.py
```

Run the comparison from the project root:

```powershell
python .\scripts\compare_claude_results.py
```

The latest comparison reported:

- **Months compared:** 18.
- **Metrics defined per month:** 13.
- **Actual value comparisons:** 209.
- **Mismatches:** 0.
- **Tolerance:** 0.01 in absolute difference.

The script compares compatible headline metrics, including revenue, COGS, gross profit, margins, operating expenses, operating income, net income, month-over-month changes, and trailing-12-month totals. Metrics unavailable in both reports for a particular month are skipped.

This result supports numerical agreement between the comparable fields in the two exported reports. It does not prove that every narrative insight, expense classification, accounting interpretation, or recommendation is correct. The comparison also depends on both report files being present locally.

The workbook-based Claude analysis is separate from the QuickBooks sandbox integration. It should not be interpreted as a completed workflow that retrieves QBO data and processes it through the Claude skill.

## QuickBooks Online Sandbox MCP Integration

The custom MCP server is located at:

```text
src/qbo_mcp_server.py
```

It uses the local OAuth credentials and token file created by:

```text
src/qbo_oauth.py
```

The MCP server is configured for the QuickBooks Online developer sandbox and refuses to start if the configured environment is not `sandbox`.

### Available MCP Tools

| Tool | Purpose |
|---|---|
| `qbo_sandbox_status` | Verifies the connection and retrieves the sandbox company name. |
| `qbo_list_accounts` | Retrieves the sandbox chart of accounts. |

### Connection Verification

The MCP connection was successfully verified against a QuickBooks developer sandbox company. The status tool returned:

- Connection status: connected.
- Environment: sandbox.
- Company information: retrieved successfully.

The chart-of-accounts tool was also exercised against the sandbox.

### Claude Desktop Configuration

The MCP server can be registered in the Claude Desktop MCP configuration using the local Python executable and the absolute path to `src/qbo_mcp_server.py`.

Example configuration structure:

```json
{
  "mcpServers": {
    "re-financial-qbo": {
      "command": "C:\\path\\to\\python.exe",
      "args": [
        "C:\\path\\to\\RE Financial\\src\\qbo_mcp_server.py"
      ]
    }
  }
}
```

Replace the example paths with the actual paths on the machine running Claude Desktop. Keep credentials in the local `.env` file; do not place them in the MCP configuration.

After editing the configuration, restart Claude Desktop and verify that the MCP server starts successfully and its tools are available.

### Token Handling

- OAuth access and refresh tokens are stored locally in `token.json`.
- Token files are excluded from Git.
- The MCP server refreshes the access token after an HTTP 401 response and persists updated token credentials.
- Token refresh and reauthorization failures should be handled without exposing credentials in logs.

### Integration Boundary

The MCP server provides read-only sandbox access through its implemented tools. It does not automatically import the Excel workbook into QuickBooks, nor does it currently connect QuickBooks data to the workbook trend-analysis pipeline. A combined end-to-end workflow using QBO data and the Claude skill remains future work.

## Evaluation and Regression Strategy

Golden cases are stored in:

```text
evals/cases/golden_cases.json
```

Regression tests should run whenever changes are made to:

- Workbook parsing.
- Financial metric calculations.
- Expense-category mappings.
- Missing-value handling.
- Output structure or schema.
- Golden-case evaluation logic.
- Client access-control behavior.

The project uses three complementary forms of validation:

1. **Unit tests:** Verify financial calculations, data-quality handling, and client-isolation behavior.
2. **Golden evaluation:** Checks calculated outputs against five predefined cases with expected values.
3. **Claude output comparison:** Checks comparable headline metrics across the 18-month local and Claude reports.

Numerical errors, unsupported claims, incorrect treatment of missing values, and failure to flag unusual results should be treated as important evaluation failures. Narrative quality should be evaluated separately using the rubric and actual model outputs.

## Architecture and Security Principles

- Separate workbook parsing, financial calculations, validation, export, and external authentication.
- Keep the reusable skill separate from deterministic calculation code.
- Preserve source values and flag questionable data for review.
- Separate credentials from application code.
- Restrict the QBO demonstration to the developer sandbox.
- Avoid storing real client financial data.
- Do not mix information or credentials between clients.
- Require human review of unusual financial movements and data-quality warnings.
- Document limitations and test failures rather than reporting unverified capabilities as complete.

### Multi-Client Considerations

The project includes an in-memory client-isolation prototype in:

```text
src/client_isolation.py
```

It provides separate in-memory datasets for registered client IDs and checks that a requesting client can retrieve only its own dataset through the public retrieval method. It also rejects duplicate registrations and unknown clients and returns defensive copies to help prevent accidental modification of stored data.

The prototype was tested with ten fictional clients. Seven automated tests passed, covering:

- Registration of ten clients.
- Access to each client's own data.
- Rejection of cross-client access.
- Rejection of unknown clients.
- Rejection of duplicate registrations.
- Protection against mutation through returned copies.
- Consistent ordering of registered client IDs.

**Security limitation:** This is an in-process demonstration, not a production security boundary. It does not implement authenticated identities, persistent tenant storage, production-grade authorization, separate per-client QuickBooks credentials, or multi-client hosting. The prototype's administrative client-listing method is intended for testing and must not be treated as an authorization mechanism.

A real multi-client deployment would require authenticated identities, server-side authorization on every request, tenant-scoped storage and queries, secure per-client credential management, audit logging, secret management, appropriate operational monitoring, and security testing. Production isolation has not been implemented or validated.

## Limitations

- Financial calculations and expense mappings should be reviewed against the supplied workbook and documented assumptions.
- Negative source values are not automatically treated as invalid; their meaning depends on the account and accounting convention.
- Golden tests validate structured calculations, not the full quality of generated narrative.
- Claude comparison validates compatible exported headline metrics, not every narrative claim or accounting interpretation.
- The QBO integration has been verified against a developer sandbox; it has not been validated against a live company.
- Automated workbook-to-QBO data loading and a combined end-to-end workflow connecting QBO data to Claude's financial analysis remain unimplemented.
- The client-isolation prototype is in-memory and does not provide production-grade tenant security.
- Production hosting, tenant authentication, persistent tenant separation, and production multi-client isolation have not been implemented or validated.

## License and Data

This repository was created for an engineering assignment. The workbook is intended to contain fictional assignment data. Do not add real financial statements, production credentials, access tokens, or confidential client information to the repository.