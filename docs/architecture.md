# Architecture Note — RE Financial Services AI Solutions Builder

## 1. Overview

The project implements a modular monthly financial analysis workflow and a separate QuickBooks Online (QBO) developer sandbox integration through the Model Context Protocol (MCP).

The financial analysis pipeline processes an Excel workbook containing 18 months of fictional financial statements. The QBO integration demonstrates sandbox authentication and read-only access to company information and the chart of accounts through Claude Desktop.

The project also includes a reusable monthly financial trend-analysis skill, a golden-case evaluation framework, a comparison script for Claude-generated and locally generated analysis results, and an in-memory client-isolation prototype.

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
        |
        v
  Claude vs. Local Comparison
  scripts/compare_claude_results.py


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
  Read-only Sandbox Status
  and Account Listing


                   Client Isolation Prototype

  Client ID
      |
      v
  ClientDataStore
  src/client_isolation.py
      |
      v
  Client-scoped in-memory data
      |
      v
  Authorization checks and
  defensive-copy protection
      |
      v
  tests/test_client_isolation.py
```

The financial analysis pipeline and QuickBooks integration are currently separate workflows. The financial analysis pipeline does not automatically retrieve data from QuickBooks, and the monthly-trend-analysis skill has not been verified end-to-end inside Claude against the supplied workbook.

The client-isolation component is a separate, in-memory prototype. It is not integrated into the QBO MCP server and does not constitute a production multi-tenant architecture.

## 3. Project Structure and Responsibilities

| Component | Responsibility |
|---|---|
| `data/financial_statements.xlsx` | Supplied fictional financial statements workbook. |
| `src/analysis/workbook_parser.py` | Reads and parses workbook data. |
| `src/analysis/trend_analyzer.py` | Calculates financial metrics, trends, trailing-12-month values, and validation flags. |
| `src/export_analysis.py` | Exports the structured local analysis report. |
| `src/validation/golden_evaluator.py` | Evaluates structured analysis results against golden-case fixtures. |
| `scripts/compare_claude_results.py` | Compares compatible headline metrics from Claude-generated and local analysis reports. |
| `skills/monthly-trend-analysis/SKILL.md` | Documents the reusable Claude skill and its expected analysis workflow. |
| `evals/cases/golden_cases.json` | Contains five evaluation scenarios and their expected results. |
| `tests/test_trend_analyzer.py` | Tests financial calculations and reconciliation behaviour. |
| `tests/test_golden_evaluator.py` | Tests golden-case evaluation and detection of expected issues. |
| `src/client_isolation.py` | Implements an in-memory client-data store with client-scoped access checks and defensive copying. |
| `tests/test_client_isolation.py` | Tests client isolation, duplicate registration, unknown clients, and data-mutation protection. |
| `src/qbo_oauth.py` | Handles the local QuickBooks OAuth flow and token storage. |
| `src/qbo_mcp_server.py` | Exposes QuickBooks sandbox operations as MCP tools. |
| `docs/testing.md` | Documents the test strategy, results, and limitations. |
| `docs/architecture.md` | Describes the architecture, security approach, verification results, and outstanding work. |
| `README.md` | Provides project setup, execution, integration, testing, and security instructions. |

## 4. MCP Integration

The custom MCP server uses the Python MCP SDK and the QuickBooks API.

### Exposed tools

- **`qbo_sandbox_status`** — verifies access to the connected sandbox company and returns company information and connection status.
- **`qbo_list_accounts`** — retrieves the chart of accounts from the sandbox.

Both tools were invoked successfully through the configured RE Financial MCP server in Claude Desktop.

The status tool returned a successful connection and confirmed the sandbox environment. The account-listing tool returned 89 accounts in the verified run. No tool errors were reported during that check.

The server is configured to reject an environment other than `sandbox`. Its implemented QuickBooks operations are read-only.

The successful MCP test verifies the sandbox status and account-listing operations. It does not establish that workbook analysis is integrated with QuickBooks or that the entire financial-analysis workflow runs end-to-end inside Claude.

### Authentication and token refresh

The local OAuth flow obtains authorization from the QuickBooks developer sandbox. Application credentials are read from `.env`, while OAuth tokens are stored locally in `token.json`.

The MCP server implements access-token refresh after an HTTP 401 response and saves updated token credentials, including a rotated refresh token when returned by the OAuth client.

Token refresh and recovery from expired or revoked authorization should be tested explicitly as part of further integration testing.

## 5. Security and Credential Handling

The current implementation follows these principles:

- Keep application secrets and configuration in `.env`.
- Keep OAuth access and refresh tokens in the local `token.json` file.
- Exclude `.env`, token files, generated reports, Python cache files, and the local MCP backup file from Git.
- Never print credentials, authorization codes, or token values in logs or reports.
- Use fictional assignment data and the QuickBooks developer sandbox only.
- Avoid live-company access without explicit authorization and a separate security review.
- Restrict the implemented QuickBooks tools to read-only operations.
- Use client-scoped access checks in the in-memory isolation prototype rather than relying only on prompts or model instructions.

The repository's Git ignore rules are intended to prevent local secrets and generated reports from being committed. These files must still be checked before every commit, because `.gitignore` does not automatically remove files that were already tracked.

The in-memory client-isolation prototype demonstrates basic access-boundary checks and protection against accidental mutation of stored data. It does not provide persistent tenant storage, authentication, production authorization, or isolation of QBO credentials between clients.

For production deployment, credentials should be stored in an appropriate secrets manager, access should follow least-privilege principles, and token storage and rotation should be reviewed for the target hosting environment. Tenant identity must be authenticated and authorized independently of model-generated instructions.

## 6. Financial Analysis and Evaluation

The analysis pipeline calculates revenue, cost of goods sold (COGS), gross profit, margins, operating expenses, operating income, net income, month-over-month changes, and trailing-12-month metrics when sufficient data is available.

Validation checks preserve source values and flag issues for review instead of silently replacing questionable data.

### Automated tests

The latest full test-suite run completed successfully:

- **17 automated tests passed**, with zero failures.
- The suite includes financial analysis, golden-evaluator, and client-isolation tests.
- The client-isolation module has seven dedicated tests covering client registration, access restrictions, unknown clients, duplicate registration, own-client access, sorted client IDs, and defensive-copy protection.

### Golden-case evaluation

The golden evaluation suite passed all five cases, with 22 expected-value checks and zero failures.

The five cases cover revenue growth, revenue decline with higher expenses, a loss-to-profit transition, a missing comparison value, and an expense-subtotal mismatch.

### Claude versus local analysis

The comparison script compares compatible headline metrics in the Claude-generated report and the local analysis report.

The latest recorded comparison reported:

- 18 months in the Claude report.
- 18 months in the local report.
- 209 actual metric-value comparisons.
- Zero mismatches within the configured tolerance of 0.01.

This comparison establishes agreement for the headline metric values included in the script. It does not verify every expense mapping, the completeness of every account classification, or the factual accuracy and quality of Claude-generated narrative.

The golden evaluator validates structured numerical outputs against expected results. It does not automatically grade the factual accuracy, clarity, or quality of model-generated commentary. Narrative evaluation remains a separate task.

## 7. Hosting and Multi-Client Separation

The current implementation is a local assignment prototype. Claude Desktop runs the MCP client, and the custom MCP server runs locally using the configured Python executable.

No production hosting or complete multi-tenant service has been implemented.

The `src/client_isolation.py` module provides an in-memory `ClientDataStore` prototype. It supports client registration, client-scoped access checks, rejection of unknown or duplicate client registrations, and defensive copying to prevent callers from mutating stored data through returned objects.

The associated seven tests pass as part of the full 17-test suite. These results verify the behaviour of the prototype's implemented checks; they do not establish production-grade security or multi-tenant isolation.

A future deployment supporting ten clients should provide:

1. Separate tenant identities and authorization boundaries.
2. Isolated OAuth credentials and tokens for each client.
3. Tenant-scoped persistent data access and storage.
4. Access controls and audit logging.
5. Centralized secret management and token rotation.
6. Secure transport, monitoring, error handling, and operational recovery.
7. Tests confirming that one client's data cannot be accessed by another client.
8. Authenticated tenant identity on every request, with authorization enforced by the service rather than by prompts alone.

The in-memory prototype is a foundation for demonstrating isolation logic, not a substitute for these production controls.

## 8. Current Limitations and Next Steps

The following work remains outside the verified implementation:

- Loading workbook data into QuickBooks.
- Connecting the QuickBooks MCP tools to the financial analysis pipeline.
- Verifying execution of the monthly-trend-analysis skill end-to-end inside Claude against the supplied workbook.
- Automatically grading actual Claude-generated narrative against the evaluation rubric.
- Deploying a production-hosted, multi-client architecture.
- Implementing persistent, authenticated tenant storage and per-client QBO credential isolation.
- Completing dedicated tests for token expiration, refresh-token rotation, revocation, and recovery.
- Investigating the sandbox account timestamp that appeared later than the date of the verification run.

These items should be treated as future work rather than completed features. The sandbox timestamp observation is recorded for investigation; its cause has not been established.

## 9. Verification Summary

| Area | Status |
|---|---|
| Workbook analysis pipeline | Implemented |
| Full automated test suite | 17 passed, 0 failures |
| Client-isolation prototype tests | 7 passed |
| Golden evaluation cases | 5 passed |
| Golden expected-value checks | 22 passed, 0 failures |
| Claude-versus-local headline comparison | 209 comparisons, 0 mismatches within configured tolerance |
| QuickBooks sandbox connection | Verified |
| MCP sandbox status tool | Successfully invoked |
| MCP account-listing tool | Successfully invoked; 89 accounts returned in the verified run |
| Implemented QBO operations | Read-only |
| Workbook-to-QuickBooks automation | Not implemented |
| End-to-end Claude skill execution against the workbook | Not verified |
| Automated grading of Claude-generated narrative | Not implemented |
| Production hosting and multi-client isolation | Not implemented |
| Token expiration and revocation recovery tests | Not completed |

## 10. Conclusion

The project demonstrates a modular financial trend-analysis pipeline, a reusable analysis skill, structured golden-case evaluation, comparison of compatible Claude and local headline metrics, a verified read-only QuickBooks sandbox integration, and a tested in-memory client-isolation prototype.

The implemented components have been tested within their documented scope. The project does not claim a complete QuickBooks-to-analysis workflow, end-to-end skill execution inside Claude, or production-ready multi-tenant deployment.

The architecture and verification results distinguish completed functionality from outstanding integration, testing, and deployment work.
