---
name: monthly-trend-analysis
description: Analyze monthly financial statement workbooks, identify revenue and expense trends, calculate month-over-month and trailing-12-month changes, validate totals, flag unusual movements, and produce a review-ready financial analysis. Use when a user supplies monthly financial statements for trend analysis.
---

# Monthly Financial Trend Analysis

## Purpose

Produce a consistent, evidence-based monthly financial trend report from a supplied financial statement workbook. The report is intended to support human review and decision-making; it is not an audit, an accounting opinion, or a substitute for professional judgment.

## Inputs

Use the supplied workbook and, when available, the structured output from the project's Python analysis pipeline.

The expected workbook contains monthly Income Statement and Balance Sheet worksheets. Do not assume that every workbook uses the same sheet names, row positions, currency, or account hierarchy without checking.

Before analysis:

1. Identify the reporting period and available worksheets.
2. Confirm that the reporting months are recognized correctly and sorted chronologically.
3. Identify reported totals separately from individual account rows.
4. Determine whether the workbook specifies a currency. If it does not, describe amounts as being in the source workbook's units without inventing a currency.
5. Identify missing values, duplicate labels, non-numeric entries, and other data-quality limitations.

If the workbook cannot be read reliably, explain the limitation and request a usable input. Do not fabricate results.

## Required analysis

### 1. Executive summary

Summarize the reporting period and the most important supported movements. Distinguish observed results from hypotheses that require investigation.

### 2. Monthly financial trends

For each available month, report:

- Revenue, using the workbook's reported total income.
- Cost of goods sold.
- Gross profit and gross margin.
- Operating expenses.
- Operating income.
- Net income and net profit margin.
- Month-over-month revenue change in absolute terms and percentage terms.
- Month-over-month net income change in absolute terms.
- Trailing-12-month revenue and net income when 12 complete months are available.

Use these formulas:

- Revenue change = current-month revenue − previous-month revenue.
- Revenue change percentage = revenue change ÷ absolute previous-month revenue × 100, provided the previous-month revenue is not zero and both values are available.
- Gross margin = gross profit ÷ revenue × 100, provided revenue is not zero and both values are available.
- Net profit margin = net income ÷ revenue × 100, provided revenue is not zero and both values are available.
- Trailing-12-month totals = sum of the latest 12 consecutive months, including the current month, only when all 12 required values are available.

If a comparison is undefined because of missing data or a zero denominator, report it as unavailable rather than inventing a percentage. Explain unusual percentage interpretations when the prior period is negative or changes sign.

### 3. Operating expense analysis

Analyze the expense categories defined by the supplied analysis pipeline or verified from the workbook's account hierarchy.

- Preserve the source account labels.
- Do not double-count parent subtotals and their underlying detail accounts.
- Do not silently omit accounts when calculating category totals.
- Compare calculated category subtotals with reported subtotals where both exist.
- Reconcile mapped expense categories against reported total operating expenses.
- Report differences above the defined tolerance and preserve both calculated and reported values.
- Treat account classifications as source-workbook classifications unless independently verified.

If the category mapping is incomplete or does not reconcile, flag the affected results and explain that the analysis is not fully validated.

### 4. Unusual movements and review flags

Identify material changes, including:

- Significant month-over-month revenue increases or decreases.
- Material changes in operating expenses.
- Transitions from net loss to net profit, or from profit to loss.
- Missing values, inconsistent totals, or reconciliation failures.
- Unexpected movements that warrant checking against underlying transactions.

Use thresholds configured by the analysis pipeline when available. If no threshold is configured, describe the movement without pretending that a specific materiality threshold was formally established.

Do not assume that an unusual value is erroneous. State what changed, why it warrants review, and what evidence a human reviewer should examine.

### 5. Human reviewer section

Include a concise checklist covering:

- Significant revenue movements and their underlying drivers.
- Large expense changes and account-level explanations.
- Profit/loss transitions and unusual monthly results.
- Reconciliation differences and missing data.
- Any assumptions or limitations that affect interpretation.

Clearly label the report as requiring human review.

## Data integrity and calculation rules

1. Prefer structured numeric outputs generated by the Python analysis pipeline over mental arithmetic.
2. Treat reported statement totals as the comparison baseline; do not silently replace them with independently calculated values.
3. Preserve negative values unless a verified rule justifies a transformation.
4. Never treat missing values as zero without an explicit, justified rule.
5. Do not invent transactions, explanations, currency, business context, or causal relationships.
6. Do not claim that a financial movement was caused by another movement merely because both occurred in the same period.
7. Round figures for presentation only; retain original precision for calculations and reconciliation.
8. Report unavailable metrics as unavailable, with the reason.
9. Clearly separate verified calculations, observations, hypotheses, and recommendations.
10. If the workbook's source values appear inconsistent, disclose the inconsistency rather than silently correcting it.

## Output format

Produce a structured report with these sections:

1. Report title and period covered.
2. Executive summary.
3. Monthly trend table.
4. Revenue and profitability commentary.
5. Operating expense category analysis.
6. Trailing-12-month analysis.
7. Data-quality and reconciliation findings.
8. Prioritized review flags.
9. Human reviewer checklist.
10. Methodology and limitations.

Use compact tables and concise commentary. Include exact periods and clearly labelled units. Avoid unsupported predictions and overly confident conclusions.

## Evaluation and regression

When golden evaluation cases are supplied:

- Compare structured numerical outputs with their expected values.
- Check all required inclusions and prohibited claims in the commentary.
- Record each case's score, failures, and evidence.
- Treat material numerical errors and invented financial facts as critical failures, regardless of the aggregate score.
- Do not claim an evaluation passed unless the case was actually executed and checked.
- Re-run the regression suite after changes to parsing, calculations, category mappings, prompts, or report formatting.

## Security and confidentiality

- Use only the authorized fictional workbook and approved developer sandbox data.
- Never request or use production accounting credentials for this workflow.
- Do not expose passwords, API keys, access tokens, or connection strings in reports, logs, or prompts.
- Keep each client's data and credentials isolated.
- Do not send financial data to external services unless the destination is authorized for that data.
- If the source, authorization, or environment is unclear, stop and request clarification.
