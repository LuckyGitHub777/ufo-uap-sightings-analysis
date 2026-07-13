from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sightings_analysis.synthetic_data import write_csv


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "sightings_analysis", *args],
            text=True,
            capture_output=True,
            check=False,
            cwd=cwd,
        )

    def test_help_lists_end_user_commands(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        for command in ("demo", "template", "validate", "analyze"):
            self.assertIn(command, result.stdout)

    def test_demo_writes_input_inside_output_and_protects_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output with spaces"
            first = self.run_cli("demo", "--output", str(output))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((output / "input" / "synthetic-reports.csv").exists())
            second = self.run_cli("demo", "--output", str(output))
            self.assertEqual(second.returncode, 4)
            forced = self.run_cli("demo", "--output", str(output), "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)

    def test_template_command_creates_csv_and_guide(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "my reports.csv"
            result = self.run_cli("template", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            guide = output.with_name("my reports-README.md")
            self.assertTrue(guide.exists())
            text = guide.read_text(encoding="utf-8")
            self.assertIn("two-letter state codes", text)
            self.assertNotIn('"\n        "', text)

    def test_validation_is_human_readable_by_default_and_json_on_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = write_csv(Path(directory) / "reports.csv", rows=10)
            human = self.run_cli("validate", "--reports", str(source))
            self.assertEqual(human.returncode, 0, human.stderr)
            self.assertIn("Validation passed", human.stdout)
            self.assertIn("Records:", human.stdout)
            machine = self.run_cli("validate", "--reports", str(source), "--json")
            self.assertEqual(machine.returncode, 0, machine.stderr)
            self.assertIn('"row_count": 10', machine.stdout)

    def test_empty_file_returns_actionable_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state,shape\n",
                encoding="utf-8",
            )
            result = self.run_cli(
                "analyze",
                "--reports",
                str(path),
                "--output",
                str(Path(directory) / "out"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Validation failed", result.stderr)
            self.assertIn("no report rows", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_single_record_generates_descriptive_output_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.csv"
            path.write_text(
                "report_id,occurred_at,reported_date,state,shape\n"
                "R1,2024-01-01T20:00,2024-01-01,CA,light\n",
                encoding="utf-8",
            )
            output = Path(directory) / "out"
            result = self.run_cli(
                "analyze",
                "--reports",
                str(path),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            summary = (output / "analysis-summary.md").read_text(encoding="utf-8")
            self.assertIn("Not calculated", summary)

    def test_invalid_file_returns_nonzero_and_helpful_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            path.write_text("report_id,state\nR1,CA\n", encoding="utf-8")
            result = self.run_cli(
                "analyze",
                "--reports",
                str(path),
                "--output",
                str(Path(directory) / "out"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Validation failed", result.stderr)
            self.assertIn("Your source file was not modified", result.stderr)

    def test_analysis_preserves_source_and_requires_material_warning_acknowledgment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = write_csv(root / "authorized reports.csv")
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            blocked = self.run_cli(
                "analyze",
                "--reports",
                str(source),
                "--output",
                str(root / "blocked output"),
            )
            self.assertEqual(blocked.returncode, 3)
            self.assertIn("material warnings", blocked.stderr.lower())
            allowed = self.run_cli(
                "analyze",
                "--reports",
                str(source),
                "--output",
                str(root / "completed output"),
                "--allow-warnings",
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            after = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
