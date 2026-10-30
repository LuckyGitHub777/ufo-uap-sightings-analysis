from __future__ import annotations

import csv
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

from . import METHODOLOGY_VERSION, __version__
from .context import AnalysisContext
from .visualization import write_figures


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _interpretation(result: dict[str, Any], context: AnalysisContext) -> str:
    if result.get("status") != "calculated":
        return f"Not calculated: {result.get('reason', 'insufficient data')}"
    if result["analysis"] == "monthly_count_period_comparison":
        return (
            "A deterministic two-sided permutation test compares monthly report counts "
            f"for the {context.short_label}. The result describes the "
            f"{'generated' if context.dataset_type == 'synthetic' else 'supplied'} records "
            "and does not establish causation or verify underlying events."
        )
    return (
        "The linear trend summarizes monthly report counts for the "
        f"{context.short_label}. It is descriptive and does not establish causation "
        "or verify underlying events."
    )


def _format_metric(value: Any) -> str:
    return "Not calculated" if value in (None, "") else str(value)


def _plain_language_interpretation(
    period: dict[str, Any],
    trend: dict[str, Any],
    context: AnalysisContext,
) -> str:
    statements: list[str] = []

    if period.get("status") == "calculated":
        p_value = float(period["permutation_p_value"])
        if p_value < 0.05:
            statements.append(
                "The difference between the two monthly-count periods is relatively "
                "unusual under the no-difference resampling model. This is statistical "
                "evidence about these records, not proof of causation or event validity."
            )
        else:
            statements.append(
                "The two monthly-count periods do not show strong evidence of a "
                "difference under the no-difference resampling model."
            )
    else:
        statements.append(
            "The period comparison was not calculated because the available monthly "
            "sequence was insufficient."
        )

    if trend.get("status") == "calculated":
        correlation = float(trend["pearson_r"])
        magnitude = abs(correlation)
        strength = "weak" if magnitude < 0.3 else "moderate" if magnitude < 0.7 else "strong"
        direction = "upward" if correlation > 0 else "downward" if correlation < 0 else "flat"
        statements.append(
            f"The simple monthly linear pattern is {strength} and {direction}. "
            f"Its R² is {trend['r_squared']}, so the fitted line is only a descriptive "
            "summary of the monthly variation."
        )
    else:
        statements.append(
            "The monthly trend was not calculated because the available monthly "
            "sequence was insufficient."
        )

    if context.dataset_type == "synthetic":
        statements.append(
            "These generated results demonstrate the software and are not findings "
            "about real-world UFO/UAP activity."
        )
    else:
        statements.append(
            "These statements describe the supplied records only and do not verify "
            "underlying events or overcome source-data limitations."
        )

    return "\n".join(f"- {statement}" for statement in statements)


def write_outputs(
    output_dir: Path,
    *,
    source_path: Path,
    validation: dict[str, Any],
    analysis: dict[str, Any],
    context: AnalysisContext,
    seed: int | None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = write_figures(output_dir / "figures", analysis, context)

    quality_path = output_dir / "data-quality-report.json"
    descriptive_path = output_dir / "descriptive-statistics.json"
    stats_path = output_dir / "statistical-results.csv"
    flow_path = output_dir / "sample-flow.csv"
    summary_path = output_dir / "analysis-summary.md"
    manifest_path = output_dir / "run-manifest.json"

    quality_path.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    descriptive = {
        key: value for key, value in analysis.items() if key != "statistical_results"
    }
    descriptive_path.write_text(
        json.dumps(descriptive, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    fieldnames = [
        "analysis",
        "status",
        "reason",
        "first_period_start",
        "first_period_end",
        "second_period_start",
        "second_period_end",
        "first_period_months",
        "second_period_months",
        "first_period_mean",
        "second_period_mean",
        "difference",
        "permutation_p_value",
        "months",
        "period_start",
        "period_end",
        "pearson_r",
        "slope_reports_per_month",
        "intercept",
        "r_squared",
        "interpretation",
    ]
    rendered_statistics: list[dict[str, Any]] = []
    for result in analysis["statistical_results"]:
        rendered = dict(result)
        rendered["interpretation"] = _interpretation(result, context)
        rendered_statistics.append(rendered)
    with stats_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rendered_statistics)

    delay = analysis["reporting_delay"]
    flow_rows = [
        {
            "stage": "Input",
            "entering": analysis["input_rows"],
            "flagged": 0,
            "excluded": 0,
            "retained": analysis["input_rows"],
            "reason": f"{context.dataset_label} records read without modification",
        },
        {
            "stage": "Validation",
            "entering": analysis["input_rows"],
            "flagged": validation["warning_count"],
            "excluded": 0,
            "retained": analysis["input_rows"],
            "reason": "Quality findings recorded; general analysis retains rows",
        },
        {
            "stage": "Temporal and geographic analysis",
            "entering": analysis["input_rows"],
            "flagged": 0,
            "excluded": 0,
            "retained": analysis["input_rows"],
            "reason": "Validated rows included",
        },
        {
            "stage": "Reporting-delay analysis",
            "entering": analysis["input_rows"],
            "flagged": delay["excluded_negative_calendar_rows"],
            "excluded": delay["excluded_negative_calendar_rows"],
            "retained": delay["valid_rows"],
            "reason": "Report date before sighting date; excluded only from reporting-delay calculations",
        },
    ]
    with flow_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["stage", "entering", "flagged", "excluded", "retained", "reason"],
        )
        writer.writeheader()
        writer.writerows(flow_rows)

    results_by_name = {
        item["analysis"]: item for item in rendered_statistics
    }
    period = results_by_name["monthly_count_period_comparison"]
    trend = results_by_name["monthly_linear_trend"]
    month_span = analysis["month_span"]
    plain_language = _plain_language_interpretation(period, trend, context)

    if period["status"] == "calculated":
        period_section = f"""### Monthly Count Statistical Demonstration

- First period: **{period['first_period_start']} through {period['first_period_end']}**
- Second period: **{period['second_period_start']} through {period['second_period_end']}**
- First-period monthly mean: **{period['first_period_mean']}**
- Second-period monthly mean: **{period['second_period_mean']}**
- Difference: **{period['difference']}**
- Permutation p-value: **{period['permutation_p_value']}**
"""
    else:
        period_section = f"""### Monthly Count Statistical Demonstration

**Not calculated:** {period['reason']}
"""

    if trend["status"] == "calculated":
        trend_section = f"""### Monthly Linear Trend

- Period: **{trend['period_start']} through {trend['period_end']}**
- Calendar months represented: **{trend['months']}**
- Pearson correlation with month index: **{trend['pearson_r']}**
- Estimated slope: **{trend['slope_reports_per_month']} reports per month**
- R²: **{trend['r_squared']}**
"""
    else:
        trend_section = f"""### Monthly Linear Trend

**Not calculated:** {trend['reason']}
"""

    if context.dataset_type == "synthetic":
        boundary = (
            "The demonstration is designed to show the pipeline and its controls. "
            "Its generated findings are not real-world UFO/UAP claims."
        )
    else:
        boundary = (
            "These results describe the user-supplied records only. They do not verify "
            "underlying events, establish causation, or overcome limitations in the source data."
        )

    summary = f"""# UFO/UAP Sightings Analysis Summary

> Start here. This report explains the most important results before presenting detailed statistics.

## At a Glance

- Dataset: **{context.dataset_label}**
- Records analyzed: **{analysis['input_rows']:,}**
- Date coverage: **{analysis['date_coverage']['start']} to {analysis['date_coverage']['end']}**
- U.S. states represented: **{analysis['unique_states']}**
- Blocking validation errors: **{validation['blocking_error_count']}**
- Validation warnings: **{validation['warning_count']}**

## What the Results Mean

{plain_language}

## Coverage and Data Quality

- Monthly sequence: **{month_span['start']} through {month_span['end']}**
- Calendar months represented: **{month_span['months_represented']}**
- Months containing reports: **{month_span['months_with_reports']}**
- Zero-report months retained in the time series: **{month_span['zero_report_months']}**

## Reporting and Record Quality

- Same-calendar-day reports: **{delay['same_day_rows']:,}**
- Long reporting delays over 29 days: **{delay['long_delay_rows']:,}**
- Reports excluded only from reporting-delay calculations because the report date came before the sighting date: **{delay['excluded_negative_calendar_rows']:,}**
- Median valid reporting delay: **{_format_metric(delay['median_valid_days'])} days**

## Detailed Statistics

{period_section}
{trend_section}
## Statistical Glossary

- **Permutation p-value:** how unusual the observed period difference would be under repeated random reassignment.
- **Pearson correlation:** the direction and strength of a simple linear pattern over time.
- **Slope:** the estimated change in reports per calendar month.
- **R²:** the proportion of monthly variation described by the simple linear trend.

## What This Does Not Establish

{boundary}

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
"""
    summary_path.write_text(summary, encoding="utf-8")

    hash_targets = [
        quality_path,
        descriptive_path,
        stats_path,
        flow_path,
        summary_path,
        *figures.values(),
    ]
    try:
        source_path.relative_to(output_dir)
    except ValueError:
        pass
    else:
        hash_targets.append(source_path)

    manifest = {
        "project_version": __version__,
        "methodology_version": METHODOLOGY_VERSION,
        "python_runtime": platform.python_version(),
        "dataset_type": context.dataset_type,
        "dataset_label": context.dataset_label,
        "source_description": context.source_description,
        "synthetic_seed": seed,
        "external_data_used": context.external_data_used,
        "input_file": source_path.relative_to(output_dir).as_posix()
        if source_path.is_relative_to(output_dir)
        else source_path.name,
        "input_sha256": validation["source_sha256"],
        "input_rows": analysis["input_rows"],
        "blocking_errors": validation["blocking_error_count"],
        "warnings": validation["warning_count"],
        "outputs": [
            {
                "path": path.relative_to(output_dir).as_posix(),
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in sorted(set(hash_targets))
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return {
        "summary": summary_path,
        "quality": quality_path,
        "descriptive": descriptive_path,
        "statistics": stats_path,
        "sample_flow": flow_path,
        "manifest": manifest_path,
        **figures,
    }
