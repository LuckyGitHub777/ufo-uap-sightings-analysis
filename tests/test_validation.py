from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from sightings_analysis.synthetic_data import write_csv
from sightings_analysis.validation import file_sha256, validate_reports


class ValidationTests(unittest.TestCase):
    def test_synthetic_fixture_passes_with_expected_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.csv"
            write_csv(path)
            result = validate_reports(path)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["row_count"], 5000)
            self.assertEqual(result["blocking_error_count"], 0)
            self.assertEqual(result["material_warning_count"], 34)

    def test_empty_dataset_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state,shape\n",
                encoding="utf-8",
            )
            result = validate_reports(path)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["blocking_errors"][0]["code"], "empty_dataset")

    def test_single_month_is_advisory_not_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state,shape\n"
                "R1,2024-01-01T20:00,2024-01-01,CA,light\n",
                encoding="utf-8",
            )
            result = validate_reports(path)
            self.assertEqual(result["status"], "passed")
            self.assertIn("limited_temporal_coverage", result["warning_summary"])
            self.assertEqual(result["material_warning_count"], 0)

    def test_missing_column_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state\n"
                "R1,2024-01-01T20:00,2024-01-01,CA\n",
                encoding="utf-8",
            )
            result = validate_reports(path)
            self.assertEqual(result["status"], "failed")
            self.assertIn("shape", result["blocking_errors"][0]["message"])

    def test_full_state_name_is_rejected_with_conversion_help(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state,shape\n"
                "R1,2024-01-01T20:00,2024-01-01,California,light\n",
                encoding="utf-8",
            )
            result = validate_reports(path)
            self.assertEqual(result["status"], "failed")
            self.assertIn("two-letter U.S.", result["blocking_errors"][0]["message"])

    def test_sensitive_free_text_column_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(
                    [
                        "report_id",
                        "occurred_at",
                        "reported_date",
                        "state",
                        "shape",
                        "narrative",
                    ]
                )
                writer.writerow(
                    ["R1", "2024-01-01T20:00", "2024-01-01", "CA", "light", "sample"]
                )
            result = validate_reports(path)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(
                result["blocking_errors"][0]["code"],
                "unsupported_sensitive_columns",
            )

    def test_validation_does_not_modify_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.csv"
            write_csv(path)
            before = file_sha256(path)
            validate_reports(path)
            self.assertEqual(before, file_sha256(path))


if __name__ == "__main__":
    unittest.main()
