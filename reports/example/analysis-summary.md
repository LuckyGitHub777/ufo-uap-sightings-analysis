# UFO/UAP Sightings Analysis Summary

> Start here. This report explains the most important results before presenting detailed statistics.

## At a Glance

- Dataset: **Synthetic demonstration**
- Records analyzed: **5,000**
- Date coverage: **2020-01-01 to 2024-12-31**
- U.S. states represented: **20**
- Blocking validation errors: **0**
- Validation warnings: **34**

## What the Results Mean

- The two monthly-count periods do not show strong evidence of a difference under the no-difference resampling model.
- The simple monthly linear pattern is weak and downward. Its R² is 0.0583, so the fitted line is only a descriptive summary of the monthly variation.
- These generated results demonstrate the software and are not findings about real-world UFO/UAP activity.

## Coverage and Data Quality

- Monthly sequence: **2020-01 through 2024-12**
- Calendar months represented: **60**
- Months containing reports: **60**
- Zero-report months retained in the time series: **0**

## Reporting and Record Quality

- Same-calendar-day reports: **2,600**
- Long reporting delays over 29 days: **200**
- Reports excluded only from reporting-delay calculations because the report date came before the sighting date: **34**
- Median valid reporting delay: **0.0 days**

## Detailed Statistics

### Monthly Count Statistical Demonstration

- First period: **2020-01 through 2022-06**
- Second period: **2022-07 through 2024-12**
- First-period monthly mean: **85.4**
- Second-period monthly mean: **81.267**
- Difference: **-4.133**
- Permutation p-value: **0.0802**

### Monthly Linear Trend

- Period: **2020-01 through 2024-12**
- Calendar months represented: **60**
- Pearson correlation with month index: **-0.2415**
- Estimated slope: **-0.1283 reports per month**
- R²: **0.0583**

## Statistical Glossary

- **Permutation p-value:** how unusual the observed period difference would be under repeated random reassignment.
- **Pearson correlation:** the direction and strength of a simple linear pattern over time.
- **Slope:** the estimated change in reports per calendar month.
- **R²:** the proportion of monthly variation described by the simple linear trend.
- **Time of day:** Morning 06:00-11:59, Afternoon 12:00-17:59, Evening 18:00-21:59, Night 22:00-05:59 (unequal spans). Because the spans differ, compare categories with care.

## What This Does Not Establish

The demonstration is designed to show the pipeline and its controls. Its generated findings are not real-world UFO/UAP claims.

## Files Created

- `data-quality-report.json`
- `descriptive-statistics.json`
- `statistical-results.csv`
- `sample-flow.csv`
- `run-manifest.json`
- `figures/reports-by-year.svg`
- `figures/reports-by-month.svg`
- `figures/reports-by-time-of-day.svg`
- `figures/reports-by-state.svg`
- `figures/reports-by-shape.svg`
- `figures/sample-flow.svg`
