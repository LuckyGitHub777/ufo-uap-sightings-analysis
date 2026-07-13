from __future__ import annotations

import csv
import hashlib
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .constants import ALLOWED_SHAPES, REQUIRED_COLUMNS, SENSITIVE_COLUMN_NAMES, STATE_CODES


def _finding(
    code: str,
    message: str,
    *,
    row: int | None = None,
    field: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "message": message}
    if row is not None:
        item["row"] = row
    if field is not None:
        item["field"] = field
    return item


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finalize(result: dict[str, Any]) -> dict[str, Any]:
    result["warning_count"] = len(result["warnings"])
    result["blocking_error_count"] = len(result["blocking_errors"])
    result["warning_summary"] = dict(
        sorted(Counter(item["code"] for item in result["warnings"]).items())
    )
    result["blocking_error_summary"] = dict(
        sorted(Counter(item["code"] for item in result["blocking_errors"]).items())
    )
    result["status"] = "passed" if not result["blocking_errors"] else "failed"
    return result


def validate_reports(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "failed",
        "source": path.name,
        "source_sha256": None,
        "row_count": 0,
        "blocking_errors": [],
        "warnings": [],
        "material_warning_count": 0,
        "columns": [],
        "date_coverage": None,
        "observed_months": 0,
    }
    if not path.exists():
        result["blocking_errors"].append(
            _finding("file_not_found", f"Report file does not exist: {path}")
        )
        return _finalize(result)
    if not path.is_file():
        result["blocking_errors"].append(
            _finding("not_a_file", f"Report path is not a file: {path}")
        )
        return _finalize(result)

    result["source_sha256"] = file_sha256(path)
    valid_occurrences: list[datetime] = []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            result["columns"] = columns
            missing = [column for column in REQUIRED_COLUMNS if column not in columns]
            if missing:
                result["blocking_errors"].append(
                    _finding(
                        "missing_required_columns",
                        "Missing required columns: " + ", ".join(missing),
                    )
                )
                return _finalize(result)

            sensitive = sorted(
                {column.strip().lower() for column in columns} & SENSITIVE_COLUMN_NAMES
            )
            if sensitive:
                result["blocking_errors"].append(
                    _finding(
                        "unsupported_sensitive_columns",
                        "This v1 pipeline does not accept sensitive or free-text columns: "
                        + ", ".join(sensitive),
                    )
                )
                return _finalize(result)

            seen_ids: set[str] = set()
            for row_number, row in enumerate(reader, start=2):
                result["row_count"] += 1
                blank_columns = [
                    column
                    for column in REQUIRED_COLUMNS
                    if not (row.get(column) or "").strip()
                ]
                for column in blank_columns:
                    result["blocking_errors"].append(
                        _finding(
                            "blank_required_value",
                            f"Required value is blank in column '{column}'.",
                            row=row_number,
                            field=column,
                        )
                    )

                report_id = (row.get("report_id") or "").strip()
                if report_id:
                    if report_id in seen_ids:
                        result["blocking_errors"].append(
                            _finding(
                                "duplicate_report_id",
                                f"Duplicate report_id: {report_id}",
                                row=row_number,
                                field="report_id",
                            )
                        )
                    seen_ids.add(report_id)

                state = (row.get("state") or "").strip().upper()
                if state and state not in STATE_CODES:
                    result["blocking_errors"].append(
                        _finding(
                            "invalid_state_code",
                            f"Unsupported state code: {state}. Use a two-letter U.S. state or DC code, such as CA or TX.",
                            row=row_number,
                            field="state",
                        )
                    )

                shape = (row.get("shape") or "").strip().lower()
                if shape and shape not in ALLOWED_SHAPES:
                    result["warnings"].append(
                        _finding(
                            "unrecognized_shape",
                            f"Shape will be grouped as 'unknown': {shape}",
                            row=row_number,
                            field="shape",
                        )
                    )

                occurred: datetime | None = None
                reported: date | None = None
                occurred_text = (row.get("occurred_at") or "").strip()
                if occurred_text:
                    try:
                        occurred = datetime.fromisoformat(occurred_text)
                        valid_occurrences.append(occurred)
                    except ValueError:
                        result["blocking_errors"].append(
                            _finding(
                                "invalid_occurred_at",
                                "occurred_at must be an ISO-8601 date-time, for example 2024-06-15T21:30.",
                                row=row_number,
                                field="occurred_at",
                            )
                        )

                reported_text = (row.get("reported_date") or "").strip()
                if reported_text:
                    try:
                        reported = date.fromisoformat(reported_text)
                    except ValueError:
                        result["blocking_errors"].append(
                            _finding(
                                "invalid_reported_date",
                                "reported_date must be an ISO-8601 calendar date, for example 2024-06-16.",
                                row=row_number,
                                field="reported_date",
                            )
                        )

                if occurred is not None and reported is not None and reported < occurred.date():
                    result["warnings"].append(
                        _finding(
                            "negative_calendar_order",
                            "reported_date occurs before the occurrence calendar date; the row remains in general analysis but is excluded from reporting-delay statistics.",
                            row=row_number,
                            field="reported_date",
                        )
                    )
                    result["material_warning_count"] += 1
    except UnicodeDecodeError:
        result["blocking_errors"].append(
            _finding("encoding_error", "The CSV must use UTF-8 encoding.")
        )
    except csv.Error as exc:
        result["blocking_errors"].append(
            _finding("csv_error", f"CSV parsing failed: {exc}")
        )

    if result["row_count"] == 0 and not result["blocking_errors"]:
        result["blocking_errors"].append(
            _finding(
                "empty_dataset",
                "The CSV contains headers but no report rows. Add at least one report before analysis.",
            )
        )

    if valid_occurrences:
        ordered = sorted(valid_occurrences)
        month_keys = {value.strftime("%Y-%m") for value in ordered}
        result["date_coverage"] = {
            "start": ordered[0].date().isoformat(),
            "end": ordered[-1].date().isoformat(),
        }
        result["observed_months"] = len(month_keys)
        if len(month_keys) < 2 and not result["blocking_errors"]:
            result["warnings"].append(
                _finding(
                    "limited_temporal_coverage",
                    "The dataset covers fewer than two observed months. Descriptive outputs will be created, but monthly statistical tests will be marked not calculated.",
                )
            )

    return _finalize(result)
