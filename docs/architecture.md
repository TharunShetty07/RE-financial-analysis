\# Architecture Note — RE Financial Services



\## 1. System Overview



The solution separates financial workbook processing, trend calculations, validation, reusable AI instructions, and QuickBooks Online (QBO) sandbox authentication into independent modules. This separation improves maintainability, testability, and security.



\## 2. Components and Data Flow



1\. \*\*Input:\*\* The supplied fictional Excel workbook is stored in `data/financial\_statements.xlsx`.

2\. \*\*Parsing:\*\* `src/analysis/workbook\_parser.py` reads the Income Statement and Balance Sheet and extracts monthly account values.

3\. \*\*Analysis:\*\* `src/analysis/trend\_analyzer.py` calculates monthly financial metrics, month-over-month changes, trailing-12-month views, expense-category trends, and review flags.

4\. \*\*Export:\*\* `src/export\_analysis.py` produces structured JSON output in the ignored `reports/` directory.

5\. \*\*Validation:\*\* `src/validation/golden\_evaluator.py` checks structured results against cases in `evals/cases/golden\_cases.json`; unit tests cover calculations and important edge cases.

6\. \*\*AI workflow:\*\* `skills/monthly-trend-analysis/SKILL.md` specifies the reusable analysis instructions, output expectations, validation rules, and human-review requirements.

7\. \*\*External authentication:\*\* `src/qbo\_oauth.py` implements a local OAuth flow to verify access to QuickBooks developer sandbox company information.



\## 3. Project Organization



\- `data/` — assignment workbook.

\- `src/analysis/` — workbook parsing and financial calculations.

\- `src/validation/` — structured golden-case evaluation.

\- `skills/` — reusable Claude skill definition.

\- `evals/cases/` — golden evaluation fixtures.

\- `tests/` — automated regression tests.

\- `docs/` — testing and architecture documentation.

\- `reports/` — generated output, excluded from Git.

\- `.env` — local credentials, excluded from Git.



\## 4. Hosting and Integration Status



The financial analysis and test suite run locally using Python. The QBO authentication flow runs locally and has successfully retrieved company information from the developer sandbox.



This verifies the sandbox OAuth flow, \*\*not\*\* a completed Claude-to-QBO integration. A Claude-compatible MCP bridge, its deployment approach, and end-to-end invocation must be implemented and tested before claiming that Claude can query QBO through this solution. The skill also needs to be executed in the intended Claude environment for end-to-end validation.



\## 5. Credentials and Data Security



\- Use only the developer sandbox and fictional assignment data.

\- Store client secrets and tokens in local environment/configuration files, never in source code or Git.

\- Use the registered redirect URI and validate OAuth responses.

\- Avoid committing screenshots that expose authorization codes, tokens, or sensitive identifiers.

\- Do not log secrets or return them in error messages.

\- Keep generated reports and temporary token files out of version control.



\## 6. Multi-Client Isolation



For a ten-client deployment, use a separate tenant identity and authorization boundary for every client. Associate credentials, tokens, accounting data, generated reports, and logs with the correct tenant. Enforce server-side tenant authorization on every request; do not rely only on a client-supplied tenant ID. Use separate credential storage and least-privilege access, prevent cross-tenant queries, and test isolation with negative authorization tests. Production hosting would also require encrypted secret storage, access-controlled logs, token rotation, monitoring, and a documented incident-response process.



\## 7. Testing and Human Review



Regression tests cover metric calculations, trailing-12-month windows, category reconciliation, missing values, profitability transitions, and golden evaluation cases. The structured evaluator does not fully score generated narrative, so Claude's commentary should also be reviewed against the rubric. Unusual financial movements and source-data inconsistencies require human review.



\## 8. Known Limitations



The current sandbox check retrieves company information only. A completed MCP integration, QBO financial-data retrieval, and full Claude-driven end-to-end run remain separate verification steps.



