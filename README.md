# RE Financial Services — Financial Analysis & AI Solutions Builder

## Project Overview

This project implements a reusable monthly financial trend analysis workflow using a supplied Excel workbook containing 18 months of fictional financial statements. It includes workbook parsing, financial metric calculations, month-over-month comparisons, trailing-12-month analysis, data-quality checks, a reusable Claude skill, and golden evaluation cases.

The project also includes a custom Model Context Protocol (MCP) server that connects Claude Desktop to a QuickBooks Online (QBO) developer sandbox using OAuth 2.0 authentication.

**Current status:** The financial analysis pipeline and golden-case evaluation suite have been implemented and tested. The QBO sandbox connection has been verified through the custom MCP server. The workbook analysis workflow and QBO integration remain separate components; automated loading of workbook data into QBO and end-to-end execution of the analysis skill inside Claude have not been completed.

## Key Features

- **Workbook parsing:** Reads the Income Statement and Balance Sheet from the supplied Excel workbook.
- **Monthly financial analysis:** Calculates revenue, cost of goods sold (COGS), gross profit, gross margin, operating expenses, operating income, net income, and net margin.
- **Trend analysis:** Calculates month-over-month changes and trailing-12-month metrics where sufficient data is available.
- **Expense analysis:** Groups expenses into categories and checks category reconciliation.
- **Data-quality checks:** Preserves source values and flags items requiring review instead of silently modifying questionable data.
- **Reusable Claude skill:** Defines expected inputs, analysis procedures, outputs, validation rules, and human-review requirements.
- **Golden evaluations:** Includes five evaluation cases covering revenue trends, expense changes, profitability transitions, missing comparison data, and reconciliation issues.
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
├── skills/
│   └── monthly-trend-analysis/
│       └── SKILL.md
├── src/
│   ├── analysis/
│   │   ├── workbook_parser.py
│   │   └── trend_analyzer.py
│   ├── validation/
│   │   └── golden_evaluator.py
│   ├── export_analysis.py
│   ├── qbo_oauth.py
│   └── qbo_mcp_server.py
├── tests/
│   ├── test_golden_evaluator.py
│   ├── test_trend_analyzer.py
│   └── inspect_marketing.py
├── .gitignore
└── README.md
```

Generated analysis reports and local OAuth token files are excluded from version control.

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

The report is generated locally and the `reports/` directory is ignored by Git.

## Running the Tests

Run the trend-analysis unit tests:

```powershell
python -m unittest tests.test_trend_analyzer -v
```

Run the golden-evaluation unit tests:

```powershell
python -m unittest tests.test_golden_evaluator -v
```

Run both test modules together:

```powershell
python -m unittest tests.test_trend_analyzer tests.test_golden_evaluator -v
```

The combined test run completed successfully with **10 tests passing**.

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

The evaluator checks structured calculated values against expected fixtures. It does **not** automatically grade Claude-generated narrative quality. Commentary, unsupported claims, explanations, and human-review recommendations require a separate review against the evaluation rubric.

## Claude Skill

The reusable skill is located at:

```text
skills/monthly-trend-analysis/SKILL.md
```

It defines the analysis procedure, expected outputs, calculation conventions, validation requirements, and human-review flags.

The skill and local analysis pipeline are available for use and testing. Full end-to-end execution of this skill inside Claude using the supplied workbook has not yet been verified and should not be represented as completed.

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

The MCP server provides read-only sandbox access through its implemented tools. It does not automatically import the Excel workbook into QuickBooks, nor does it currently connect QuickBooks data to the workbook trend-analysis pipeline. End-to-end skill execution using QBO data inside Claude remains future work.

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

The current project is a local assignment implementation, not a production multi-tenant service. A future deployment supporting multiple clients would require explicit tenant isolation, separate authorization and credential storage for each client, access controls, audit logging, secure secret management, and appropriate operational monitoring.

## Limitations

- Financial calculations and expense mappings should be reviewed against the supplied workbook and documented assumptions.
- Negative source values are not automatically treated as invalid; their meaning depends on the account and accounting convention.
- Golden tests validate structured calculations, not the full quality of generated narrative.
- The QBO integration has been verified against a developer sandbox; it has not been validated against a live company.
- Automated workbook-to-QBO data loading and end-to-end Claude skill execution remain unimplemented.
- Production hosting and multi-client isolation have not been implemented or validated.

## License and Data

This repository was created for an engineering assignment. The workbook is intended to contain fictional assignment data. Do not add real financial statements, production credentials, access tokens, or confidential client information to the repository.
