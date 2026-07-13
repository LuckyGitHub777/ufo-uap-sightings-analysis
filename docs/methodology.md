# Methodology

## Validation Before Analysis

The pipeline validates schema, dates, identifiers, categories, duplicates, row count, U.S. state codes, and potentially sensitive columns before generating results.

## Date Semantics

`occurred_at` contains a date and time. `reported_date` contains a calendar date. Reporting delay is calculated by comparing calendar dates directly, preventing same-day evening records from being mislabeled as negative delays.

## Quality Flags

Rows with a report date earlier than the occurrence date remain available for general temporal and geographic analysis. They are excluded only from reporting-delay statistics and are disclosed in `sample-flow.csv`.

Long reporting delays remain in the dataset and are reported rather than silently deleted.

## Complete Monthly Sequence

The monthly statistical series includes every calendar month from the first through the last occurrence date. Months with zero reports remain present as zero rather than disappearing.

The report discloses:

- total calendar months represented,
- months containing reports,
- zero-report months,
- exact period boundaries used in the comparison.

## Sparse Data

- Zero-row datasets fail validation with an actionable message.
- One-row and one-month datasets receive descriptive outputs.
- Monthly statistics that lack sufficient coverage are marked `not_calculated` with a reason.
- Anticipated data conditions do not expose raw tracebacks.

## Temporal Analysis

The pipeline generates counts by year, calendar month, time of day, U.S. state, and standardized reported shape.

## Statistical Demonstration

When at least two calendar months are present, the example runs:

1. A deterministic two-sided permutation test comparing monthly report counts across two disclosed time periods.
2. A simple linear regression and Pearson correlation describing the monthly count trend.

These calculations are a first-pass statistical demonstration, not a general causal model. User-defined comparison dates are planned for a future release.

## Dataset Context

Every Markdown report, CSV interpretation, run manifest, SVG title, SVG description, footer, and sample-flow note identifies whether the analysis used:

- a synthetic demonstration, or
- a user-supplied dataset.

## Reproducibility

The demo uses a fixed seed, stable row ordering, deterministic statistical sampling, structured output files, and a run manifest with file hashes.
