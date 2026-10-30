# Example Analysis Experience

> Start here to explore the complete synthetic demonstration without installing or running anything.

This directory contains generated example records and outputs that demonstrate the software’s behavior. It does not contain real witness reports, and its results are not real-world UFO/UAP findings.

## Begin With the Summary

Open [`analysis-summary.md`](analysis-summary.md).

It explains:

- what the demonstration data represents,
- what the results mean in plain language,
- how many records were used,
- which records were treated differently for reporting-delay calculations,
- the detailed statistics,
- what the results do not establish,
- and which supporting files were created.

## Explore the Figures

| Figure | What it demonstrates |
|---|---|
| [Reports by shape](figures/reports-by-shape.svg) | Standardized reported-shape categories |
| [Reports by year](figures/reports-by-year.svg) | Complete-period temporal counts |
| [Reports by month](figures/reports-by-month.svg) | Calendar-month distribution |
| [Reports by time of day](figures/reports-by-time-of-day.svg) | Derived time-of-day categories |
| [Reports by state](figures/reports-by-state.svg) | State-coded geographic analysis |
| [How the records were used](figures/sample-flow.svg) | Visible, analysis-specific record accounting |

## Understand the 5,000-to-4,966 Difference

All 5,000 generated reports remain in general analysis.

Thirty-four generated records have a report date earlier than the reported sighting date. They remain visible in the quality report and are excluded only from reporting-delay calculations. That calculation therefore uses 4,966 records.

## Supporting Evidence

- [`data-quality-report.json`](data-quality-report.json): validation findings
- [`descriptive-statistics.json`](descriptive-statistics.json): descriptive results
- [`statistical-results.csv`](statistical-results.csv): detailed statistical output
- [`sample-flow.csv`](sample-flow.csv): machine-readable record accounting
- [`run-manifest.json`](run-manifest.json): file hashes and reproducibility information

## Continue

Return to the [main repository guide](../../README.md) to run the demonstration or analyze an authorized five-column CSV.
