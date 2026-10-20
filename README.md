\# RE Financial Services — Financial Analysis \& AI Solutions Builder



\## Project Overview



This project implements a reusable monthly financial trend analysis workflow using a supplied Excel workbook containing 18 months of fictional financial statements. It includes workbook parsing, financial metric calculations, month-over-month comparisons, trailing-12-month analysis, validation checks, a reusable Claude skill, and golden test cases.



The project also includes a local QuickBooks Online (QBO) \*\*developer sandbox OAuth connection flow\*\* to demonstrate secure authentication and verify access to sandbox company information.



> \*\*Scope note:\*\* The QBO sandbox connection has been verified by retrieving company information. A complete Claude-to-QBO MCP integration and end-to-end execution of the skill through Claude must be verified separately before claiming they are implemented.



\## Key Features



\- \*\*Workbook parsing:\*\* Reads the Income Statement and Balance Sheet from the supplied Excel workbook.

\- \*\*Monthly financial analysis:\*\* Calculates revenue, cost of goods sold (COGS), gross profit, gross margin, operating expenses, operating income, net income, and net margin.

\- \*\*Trend analysis:\*\* Calculates month-over-month changes and trailing-12-month metrics where sufficient data is available.

\- \*\*Expense analysis:\*\* Groups expenses into categories and checks category reconciliation.

\- \*\*Data-quality checks:\*\* Preserves source values and flags items requiring review rather than silently changing the data.

\- \*\*Reusable Claude skill:\*\* Defines the expected inputs, analysis workflow, outputs, validation rules, and human-review requirements.

\- \*\*Golden evaluations:\*\* Includes five evaluation cases for important trends, missing values, profitability transitions, and reconciliation issues.

\- \*\*QuickBooks sandbox authentication:\*\* Implements a local OAuth flow and verifies access by retrieving sandbox company information.



\## Project Structure



```text

RE Financial/

├── data/

│   └── financial\_statements.xlsx

├── docs/

│   └── testing.md

├── evals/

│   └── cases/

│       └── golden\_cases.json

├── skills/

│   └── monthly-trend-analysis/

│       └── SKILL.md

├── src/

│   ├── analysis/

│   │   ├── workbook\_parser.py

│   │   └── trend\_analyzer.py

│   ├── validation/

│   │   └── golden\_evaluator.py

│   ├── export\_analysis.py

│   └── qbo\_oauth.py

├── tests/

│   ├── test\_golden\_evaluator.py

│   ├── test\_trend\_analyzer.py

│   └── inspect\_marketing.py

├── .gitignore

└── README.md

```



\## Requirements



\- Python 3.11 or compatible version

\- pip

\- QuickBooks Online developer sandbox credentials for the OAuth demonstration

\- The supplied fictional financial statements workbook



\## Setup



Open PowerShell in the project root directory.



Install the required Python packages:



```powershell

python -m pip install openpyxl flask intuit-oauth requests python-dotenv

```



Ensure the supplied workbook is available at:



```text

data/financial\_statements.xlsx

```



\### Environment Configuration



Create a local `.env` file in the project root containing the QuickBooks developer sandbox credentials and redirect configuration required by `src/qbo\_oauth.py`.



Use the environment variable names expected by the implementation. Configure the redirect URI to match the URI registered in the QuickBooks developer application.



\*\*Security requirements:\*\*

\- Never commit `.env` or other credential files.

\- Never hardcode client secrets, access tokens, or refresh tokens.

\- Use sandbox credentials and fictional data only.

\- Keep OAuth callback URLs and screenshots free of authorization codes and tokens before sharing them.



The `.gitignore` file excludes environment files, Python cache files, token files, and generated reports.



\## Running the Financial Analysis



From the project root, run:



```powershell

python src/export\_analysis.py

```



The analysis export is written to:



```text

reports/monthly\_analysis.json

```



The `reports/` directory is ignored by Git because generated analysis output is kept separate from the source code.



\## Running the Tests



Run the trend-analysis unit tests:



```powershell

python -m unittest tests.test\_trend\_analyzer -v

```



Run the golden-evaluation tests:



```powershell

python -m unittest tests.test\_golden\_evaluator -v

```



Run both test modules together:



```powershell

python -m unittest tests.test\_trend\_analyzer tests.test\_golden\_evaluator -v

```



The test suite checks metric calculations, trailing-12-month windows, expense-category reconciliation, missing values, profitability transitions, and golden-case validation.



The golden evaluator checks structured expected values. It does not independently grade the quality of Claude-generated narrative; narrative quality requires a separate review against the rubric.



\## Claude Skill



The reusable skill is located at:



```text

skills/monthly-trend-analysis/SKILL.md

```



It defines the monthly analysis procedure, expected outputs, calculation conventions, validation requirements, and human-review flags.



The skill should be tested in the intended Claude environment before claiming successful end-to-end execution.



\## QuickBooks Online Sandbox



The local OAuth implementation is located at:



```text

src/qbo\_oauth.py

```



The demonstrated flow authenticates against the QuickBooks developer sandbox and retrieves company information to verify the connection.



\*\*Current integration boundary:\*\* successful sandbox authentication and company-information retrieval do not, by themselves, establish a working MCP server or a Claude-to-QBO connection. Those components require separate implementation and verification if they are part of the final deliverable.



\## Evaluation Strategy



The golden cases are stored in:



```text

evals/cases/golden\_cases.json

```



The suite covers five scenarios:



1\. Revenue increase.

2\. Revenue decline alongside rising expenses.

3\. Loss-to-profit transition.

4\. Missing prior-month revenue.

5\. Marketing subtotal mismatch.



Regression testing should run whenever the parser, metric calculations, expense mappings, or output schema changes. Numerical correctness and unsupported claims should be treated as critical evaluation criteria.



\## Architecture and Security Principles



\- Keep parsing, financial calculations, validation, and external authentication in separate modules.

\- Preserve source data and flag questionable values for review.

\- Separate credentials from application code.

\- Use only the developer sandbox for the QuickBooks demonstration.

\- Avoid storing real client data or mixing data between clients.

\- Require human review of unusual financial movements and data-quality warnings.

\- Document limitations and test failures rather than reporting unverified capabilities as complete.



\## Limitations



\- Financial calculations and category mappings should be reviewed against the supplied workbook and documented assumptions.

\- Negative values are not automatically treated as invalid; their meaning depends on the source account and accounting convention.

\- Golden tests validate structured outputs but do not fully automate qualitative assessment of generated commentary.

\- A successful QBO sandbox company-information request is not equivalent to a completed MCP integration.

\- Any multi-client production deployment would require additional isolation, authorization, logging, and operational security controls.



\## License and Data



This repository was created for an engineering assignment. The workbook is intended to contain fictional assignment data. Do not add real financial statements, production credentials, access tokens, or confidential client information to the repository.



