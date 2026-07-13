# Methodology Audit

A later V&V review reproduced the original workflow and identified several material issues.

## Date Semantics

A date-only report field had been interpreted as midnight and subtracted from an occurrence timestamp. Same-calendar-day evening reports therefore appeared negative. The corrected pipeline compares calendar dates.

## Hidden Sample Attrition

Rows marked invalid for reporting-delay purposes had also been removed from unrelated exploratory analyses. The corrected pipeline retains rows for general analysis and scopes exclusions to the analysis that requires them.

## Outlier Treatment

Long reporting delays had been removed through a global IQR rule, which constrained the observed delay range. The corrected pipeline retains long-tail records and reports quality flags instead of silently deleting them.

## Geographic Identifier Matching

The original sighting data and reference tables used inconsistent state identifiers. Exact joins reached only a small accidental subset. The corrected architecture standardizes identifiers and requires coverage disclosure before interpreting joined analyses.

## Hypothesis Alignment

An original period test compared the numeric year values attached to individual records rather than the report counts requested by the research question. The corrected statistical demonstration compares monthly counts.

## Meaning of the Audit

The original code was reproducible, but reproducibility alone did not validate the analytical design. The public version converts those lessons into validation rules, sample-flow reporting, tests, and interpretation boundaries.
