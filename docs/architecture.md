# Architecture Note — RE Financial Services AI Solutions Builder

## 1. Overview

The project implements a modular monthly financial analysis workflow and a separate QuickBooks Online (QBO) developer sandbox integration through the Model Context Protocol (MCP).

The financial analysis pipeline processes an Excel workbook containing 18 months of fictional financial statements. The QBO integration demonstrates sandbox authentication and read-only access to company information and the chart of accounts through Claude Desktop.

The implementation prioritizes deterministic calculations, validation, credential protection, testability, and explicit documentation of limitations.

## 2. Architecture

```text
                    Financial Analysis Pipeline

  Excel Workbook
        |
        v
  Workbook Parser
  src/analysis/workbook_parser.py
        |
        v
  Trend Analyzer
  src/analysis/trend_analyzer.py
        |
        v
  Analysis Export
  src/export_analysis.py
        |
        v
  monthly_analysis.json


                 QuickBooks Sandbox Integration

  QuickBooks Developer Sandbox
        |
        | OAuth 2.0
        v
  Local OAuth Flow
  src/qbo_oauth.py
        |
        v
  Local Token Storage
  token.json
        |
        v
  Custom MCP Server
  src/qbo_mcp_server.py
        |
        v
  Claude Desktop
        |
        v
  Sandbox Status and Account Listing
```

The two workflows are currently separate. The financial analysis pipeline does not automatically retrieve data from QuickBooks, and the analysis skill has not been executed end-to-end inside Claude.

## 3. Project Structure and Responsibilities

| Component | Responsibility |
|---|---|
| `data/financial_statements.xlsx` | Supplied fictional financial statements workbook. |
| `src/analysis/workbook_parser.py` | Reads and parses workbook data. |
| `src/analysis/trend_analyzer.py` | Calculates financial metrics, trends, trailing-12-month values, and validation flags. |
| `src/export_analysis.py` | Exports the structured analysis report. |
| `src/validation/golden_evaluator.py` | Evaluates structured analysis results against golden-case fixtures. |
| `skills/monthly-trend-analysis/SKILL.md` | Documents the reusable Claude skill and its expected workflow. |
| `evals/cases/golden_cases.json` | Contains five evaluation scenarios and their expected results. |
| `tests/test_trend_analyzer.py` | Tests financial calculations and reconciliation behaviour. |
| `tests/test_golden_evaluator.py` | Tests golden-case evaluation and detection of expected issues. |
| `src/qbo_oauth.py` | Handles the local QuickBooks OAuth flow and token storage. |
| `src/qbo_mcp_server.py` | Exposes QuickBooks sandbox operations as MCP tools. |
| `docs/testing.md` | Documents the test strategy, results, and limitations. |
| `README.md` | Provides setup, execution, integration, and security instructions. |

## 4. MCP Integration

The custom MCP server uses the Python MCP SDK and the QuickBooks API.

### Exposed tools

- **`qbo_sandbox_status`** — verifies access to the connected sandbox company and returns its name and connection status.
- **`qbo_list_accounts`** — retrieves the chart of accounts from the sandbox.

The connection was verified successfully through the MCP server. The status tool returned a successful connection and sandbox company information. The account-listing tool was also exercised.

The server is configured to reject an environment other than `sandbox`. Its implemented QuickBooks operations are read-only.

### Authentication and token refresh

The local OAuth flow obtains authorization from the QuickBooks developer sandbox. Credentials are read from `.env`, while OAuth tokens are stored in the local `token.json` file.

The MCP server implements access-token refresh after an HTTP 401 response and saves updated token credentials, including a rotated refresh token when returned by the OAuth client.

Token refresh and recovery from expired or revoked authorization should be tested explicitly as part of further integration testing.

## 5. Security and Credential Handling

The current implementation follows these principles:

- Keep client secrets and application configuration in `.env`.
- Keep OAuth access and refresh tokens in `token.json`.
- Exclude `.env`, token files, generated reports, Python cache files, and the local MCP backup file from Git.
- Never print credentials, authorization codes, or token values.
- Use fictional assignment data and the QuickBooks developer sandbox only.
- Avoid live-company access without explicit authorization and a separate security review.

For production deployment, credentials should be stored in an appropriate secrets manager, access should follow least-privilege principles, and token storage and rotation should be reviewed for the target hosting environment.

## 6. Financial Analysis and Evaluation

The analysis pipeline calculates revenue, COGS, gross profit, margins, operating expenses, operating income, net income, month-over-month changes, and trailing-12-month metrics when enough data is available.

Validation checks preserve source values and flag issues for review instead of silently replacing questionable data.

The latest local test run passed all 10 unit tests. The golden evaluation suite passed all five cases, with 22 expected-value checks and zero failures.

The golden evaluator validates structured calculations. It does not automatically grade the factual accuracy, clarity, or quality of Claude-generated narrative. Model-generated commentary requires separate evaluation against the rubric.

## 7. Hosting and Multi-Client Separation

The current implementation is a local assignment prototype. Claude Desktop runs the MCP client, and the custom MCP server runs locally using the configured Python executable.

No production hosting or multi-tenant service has been implemented.

A future deployment supporting ten clients should provide:

1. Separate tenant identities and authorization boundaries.
2. Isolated OAuth credentials and tokens for each client.
3. Tenant-scoped data access and storage.
4. Access controls and audit logging.
5. Centralized secret management and token rotation.
6. Secure transport, monitoring, error handling, and operational recovery.
7. Tests confirming that one client's data cannot be accessed by another client.

A shared service should identify and authorize the tenant for every request rather than relying only on prompts or model instructions to maintain separation.

## 8. Current Limitations and Next Steps

The following work remains outside the verified implementation:

- Loading workbook data into QuickBooks.
- Connecting the QuickBooks MCP tools to the financial analysis pipeline.
- Running the monthly-trend-analysis skill end-to-end inside Claude against the supplied workbook.
- Automatically grading actual Claude-generated narrative against the evaluation rubric.
- Deploying a production-hosted, multi-client architecture.
- Completing dedicated tests for token expiration, refresh-token rotation, revocation, and recovery.

These items should be treated as future work rather than completed features.

## 9. Verification Summary

| Area | Status |
|---|---|
| Workbook analysis pipeline | Implemented |
| Unit tests | 10 passed |
| Golden evaluation cases | 5 passed |
| Golden expected-value checks | 22 passed, 0 failures |
| QuickBooks sandbox connection | Verified |
| MCP sandbox status tool | Verified |
| MCP account-listing tool | Exercised |
| Workbook-to-QuickBooks automation | Not implemented |
| End-to-end Claude skill execution | Not verified |
| Production hosting and multi-client isolation | Not implemented |
