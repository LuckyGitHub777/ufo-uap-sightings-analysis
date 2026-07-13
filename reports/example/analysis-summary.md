# UFO/UAP Sightings Analysis Summary

## Scope

- Dataset: **Synthetic demonstration**
- Records analyzed: **5,000**
- Date coverage: **2020-01-01 to 2024-12-31**
- U.S. states represented: **20**
- Blocking validation errors: **0**
- Validation warnings: **34**

## Calendar Coverage

- Monthly sequence: **2020-01 through 2024-12**
- Calendar months represented: **60**
- Months containing reports: **60**
- Zero-report months retained in the time series: **0**

## Descriptive Results

- Same-calendar-day reports: **2,600**
- Long reporting delays over 29 days: **200**
- Negative calendar-order rows excluded only from delay statistics: **34**
- Median valid reporting delay: **0.0 days**

## Statistical Results

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

## Interpretation Boundary

The demonstration is designed to show the pipeline and its controls. Its generated findings are not real-world UFO/UAP claims.

## Output Inventory

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
