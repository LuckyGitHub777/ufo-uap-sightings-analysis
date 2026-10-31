from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any

from .constants import ALLOWED_SHAPES, time_of_day
from .stats import mean, pearson_r, permutation_p_value, simple_linear_regression


def _month_key(value: datetime) -> str:
    return value.strftime("%Y-%m")


def _month_sequence(start: datetime, end: datetime) -> list[str]:
    year, month = start.year, start.month
    end_pair = (end.year, end.month)
    keys: list[str] = []
    while (year, month) <= end_pair:
        keys.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return keys


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for source in csv.DictReader(handle):
            occurred = datetime.fromisoformat(source["occurred_at"].strip())
            reported = date.fromisoformat(source["reported_date"].strip())
            shape = source["shape"].strip().lower()
            rows.append(
                {
                    "report_id": source["report_id"].strip(),
                    "occurred_at": occurred,
                    "reported_date": reported,
                    "state": source["state"].strip().upper(),
                    "shape": shape if shape in ALLOWED_SHAPES else "unknown",
                    "delay_days": (reported - occurred.date()).days,
                    "time_of_day": time_of_day(occurred.hour),
                }
            )
    return rows


def _not_calculated(name: str, reason: str) -> dict[str, Any]:
    return {
        "analysis": name,
        "status": "not_calculated",
        "reason": reason,
    }


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("The dataset contains no reports to analyze.")

    ordered = sorted(rows, key=lambda row: row["occurred_at"])
    by_year = Counter(str(row["occurred_at"].year) for row in rows)
    by_month = Counter(row["occurred_at"].strftime("%b") for row in rows)
    by_time = Counter(row["time_of_day"] for row in rows)
    by_state = Counter(row["state"] for row in rows)
    by_shape = Counter(row["shape"] for row in rows)

    valid_delays = [row["delay_days"] for row in rows if row["delay_days"] >= 0]
    negative_delay_count = sum(1 for row in rows if row["delay_days"] < 0)
    same_day_count = sum(1 for row in rows if row["delay_days"] == 0)
    long_delay_count = sum(1 for row in rows if row["delay_days"] > 29)

    start = ordered[0]["occurred_at"]
    end = ordered[-1]["occurred_at"]
    month_keys = _month_sequence(start, end)
    observed_monthly_counts = Counter(_month_key(row["occurred_at"]) for row in rows)
    monthly_series = {key: observed_monthly_counts.get(key, 0) for key in month_keys}
    monthly_values = [float(value) for value in monthly_series.values()]
    observed_months = sum(1 for value in monthly_values if value > 0)
    zero_report_months = len(monthly_values) - observed_months

    statistical_results: list[dict[str, Any]] = []
    if len(monthly_values) >= 2:
        split = max(1, len(monthly_values) // 2)
        first_period = monthly_values[:split]
        second_period = monthly_values[split:]
        period_p = permutation_p_value(first_period, second_period)
        statistical_results.append(
            {
                "analysis": "monthly_count_period_comparison",
                "status": "calculated",
                "reason": "",
                "first_period_start": month_keys[0],
                "first_period_end": month_keys[split - 1],
                "second_period_start": month_keys[split],
                "second_period_end": month_keys[-1],
                "first_period_months": len(first_period),
                "second_period_months": len(second_period),
                "first_period_mean": round(mean(first_period), 3),
                "second_period_mean": round(mean(second_period), 3),
                "difference": round(mean(second_period) - mean(first_period), 3),
                "permutation_p_value": round(period_p, 4),
            }
        )

        month_index = [float(index) for index in range(len(monthly_values))]
        trend_r = pearson_r(month_index, monthly_values)
        slope, intercept, r_squared = simple_linear_regression(month_index, monthly_values)
        statistical_results.append(
            {
                "analysis": "monthly_linear_trend",
                "status": "calculated",
                "reason": "",
                "months": len(monthly_values),
                "period_start": month_keys[0],
                "period_end": month_keys[-1],
                "pearson_r": round(trend_r, 4),
                "slope_reports_per_month": round(slope, 4),
                "intercept": round(intercept, 4),
                "r_squared": round(r_squared, 4),
            }
        )
    else:
        reason = "At least two calendar months are required for monthly statistical calculations."
        statistical_results.append(_not_calculated("monthly_count_period_comparison", reason))
        statistical_results.append(_not_calculated("monthly_linear_trend", reason))

    return {
        "input_rows": len(rows),
        "date_coverage": {
            "start": start.date().isoformat(),
            "end": end.date().isoformat(),
        },
        "month_span": {
            "start": month_keys[0],
            "end": month_keys[-1],
            "months_represented": len(month_keys),
            "months_with_reports": observed_months,
            "zero_report_months": zero_report_months,
        },
        "monthly_series": monthly_series,
        "unique_states": len(by_state),
        "by_year": dict(sorted(by_year.items())),
        "by_month": {
            month: by_month.get(month, 0)
            for month in (
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            )
        },
        "by_time_of_day": {
            key: by_time.get(key, 0)
            for key in ("Morning", "Afternoon", "Evening", "Night")
        },
        "by_state": dict(by_state.most_common()),
        "by_shape": dict(by_shape.most_common()),
        "reporting_delay": {
            "valid_rows": len(valid_delays),
            "excluded_negative_calendar_rows": negative_delay_count,
            "same_day_rows": same_day_count,
            "long_delay_rows": long_delay_count,
            "median_valid_days": median(valid_delays) if valid_delays else None,
            "mean_valid_days": (
                round(mean([float(value) for value in valid_delays]), 3)
                if valid_delays
                else None
            ),
        },
        "statistical_results": statistical_results,
    }
