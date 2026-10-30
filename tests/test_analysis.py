from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from sightings_analysis.analysis import analyze_rows, load_rows
from sightings_analysis.context import AnalysisContext
from sightings_analysis.reporting import write_outputs
from sightings_analysis.synthetic_data import DEFAULT_SEED, write_csv
from sightings_analysis.validation import validate_reports


class AnalysisTests(unittest.TestCase):
    def _write_rows(self, path: Path, rows: list[list[str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["report_id", "occurred_at", "reported_date", "state", "shape"])
            writer.writerows(rows)

    def test_calendar_day_delay_is_not_negative_for_same_day_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.csv"
            self._write_rows(
                path,
                [["R1", "2024-06-15T23:30", "2024-06-15", "CA", "light"]],
            )
            analysis = analyze_rows(load_rows(path))
            self.assertEqual(analysis["reporting_delay"]["same_day_rows"], 1)
            self.assertEqual(
                analysis["reporting_delay"]["excluded_negative_calendar_rows"], 0
            )

    def test_missing_calendar_month_is_zero_filled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.csv"
            self._write_rows(
                path,
                [
                    ["R1", "2024-01-15T20:00", "2024-01-16", "CA", "light"],
                    ["R2", "2024-03-15T20:00", "2024-03-16", "TX", "circle"],
                ],
            )
            analysis = analyze_rows(load_rows(path))
            self.assertEqual(
                analysis["monthly_series"],
                {"2024-01": 1, "2024-02": 0, "2024-03": 1},
            )
            self.assertEqual(analysis["month_span"]["zero_report_months"], 1)

    def test_single_month_produces_descriptive_results_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.csv"
            self._write_rows(
                path,
                [["R1", "2024-01-15T20:00", "2024-01-16", "CA", "light"]],
            )
            analysis = analyze_rows(load_rows(path))
            self.assertEqual(analysis["input_rows"], 1)
            self.assertTrue(
                all(
                    result["status"] == "not_calculated"
                    for result in analysis["statistical_results"]
                )
            )

    def test_output_bundle_contains_six_figures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_csv(root / "reports.csv")
            validation = validate_reports(source)
            analysis = analyze_rows(load_rows(source))
            files = write_outputs(
                root / "out",
                source_path=source,
                validation=validation,
                analysis=analysis,
                context=AnalysisContext.synthetic_demo(),
                seed=DEFAULT_SEED,
            )
            for key in (
                "reports_by_year",
                "reports_by_month",
                "reports_by_time",
                "reports_by_state",
                "reports_by_shape",
                "sample_flow",
            ):
                self.assertTrue(files[key].exists(), key)

    def test_user_outputs_never_claim_synthetic_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "reports.csv"
            self._write_rows(
                source,
                [
                    ["R1", "2024-01-15T20:00", "2024-01-16", "CA", "light"],
                    ["R2", "2024-02-15T20:00", "2024-02-16", "TX", "circle"],
                ],
            )
            validation = validate_reports(source)
            analysis = analyze_rows(load_rows(source))
            output = root / "out"
            write_outputs(
                output,
                source_path=source,
                validation=validation,
                analysis=analysis,
                context=AnalysisContext.user_supplied(),
                seed=None,
            )
            public_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in output.rglob("*")
                if path.is_file() and path.suffix in {".md", ".csv", ".svg", ".json"}
            )
            self.assertIn("User-supplied dataset", public_text)
            self.assertNotIn("Synthetic demo", public_text)
            self.assertNotIn("synthetic result", public_text)

    def test_sample_flow_uses_plain_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_csv(root / "reports.csv")
            validation = validate_reports(source)
            analysis = analyze_rows(load_rows(source))
            files = write_outputs(
                root / "out",
                source_path=source,
                validation=validation,
                analysis=analysis,
                context=AnalysisContext.synthetic_demo(),
                seed=DEFAULT_SEED,
            )
            text = files["sample_flow"].read_text(encoding="utf-8")
            self.assertIn("How the Demo Records Were Used", text)
            self.assertIn("excluded from this calculation only", text)
            self.assertNotIn("calendar-order flags excluded", text)
            self.assertNotIn("\\n", text)
            import xml.etree.ElementTree as ET
            ET.parse(files["sample_flow"])

    def test_summary_includes_plain_language_interpretation_and_glossary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_csv(root / "reports.csv")
            validation = validate_reports(source)
            analysis = analyze_rows(load_rows(source))
            files = write_outputs(
                root / "out",
                source_path=source,
                validation=validation,
                analysis=analysis,
                context=AnalysisContext.synthetic_demo(),
                seed=DEFAULT_SEED,
            )
            text = files["summary"].read_text(encoding="utf-8")
            self.assertIn("## What the Results Mean", text)
            self.assertIn("## Detailed Statistics", text)
            self.assertIn("## Statistical Glossary", text)
            self.assertIn("## What This Does Not Establish", text)
            self.assertIn("## Files Created", text)
            self.assertIn("not findings about real-world UFO/UAP activity", text)
            self.assertNotIn("\\n- ", text)
            self.assertIn("\n- The simple monthly linear pattern", text)
            self.assertLess(text.index("## What the Results Mean"), text.index("## Detailed Statistics"))

    def test_machine_outputs_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_csv(root / "reports.csv")
            validation = validate_reports(source)
            analysis = analyze_rows(load_rows(source))
            for name in ("one", "two"):
                write_outputs(
                    root / name,
                    source_path=source,
                    validation=validation,
                    analysis=analysis,
                    context=AnalysisContext.synthetic_demo(),
                    seed=DEFAULT_SEED,
                )
            one = {
                path.relative_to(root / "one").as_posix(): path.read_bytes()
                for path in (root / "one").rglob("*")
                if path.is_file()
            }
            two = {
                path.relative_to(root / "two").as_posix(): path.read_bytes()
                for path in (root / "two").rglob("*")
                if path.is_file()
            }
            self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()
