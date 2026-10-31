from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sightings_analysis.integrity import verify_manifest
from sightings_analysis.privacy import scan

ROOT = Path(__file__).resolve().parents[1]


class PublicBoundaryTests(unittest.TestCase):
    def test_repository_scan_passes(self) -> None:
        self.assertEqual(scan(ROOT), [])

    def test_scan_detects_email_like_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                "contact" + chr(64) + "example.invalid",
                encoding="utf-8",
            )
            self.assertTrue(scan(root))

    def test_scan_detects_prohibited_raw_data_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data" / "raw" / "reports.csv"
            path.parent.mkdir(parents=True)
            path.write_text("report_id\nR1\n", encoding="utf-8")
            self.assertTrue(scan(root))

    def test_scan_detects_coordinate_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "coords.csv").write_text(
                "report_id,latitude,longitude\nR1,1.0,2.0\n", encoding="utf-8"
            )
            findings = scan(root)
            self.assertTrue(any("latitude" in item for item in findings))

    def test_scanner_and_validator_share_column_policy(self) -> None:
        from sightings_analysis.constants import SENSITIVE_COLUMN_NAMES
        from sightings_analysis.privacy import PROHIBITED_DATA_COLUMNS

        self.assertEqual(set(PROHIBITED_DATA_COLUMNS), set(SENSITIVE_COLUMN_NAMES))

    def test_public_scanner_has_no_embedded_private_term_table(self) -> None:
        source = (ROOT / "sightings_analysis" / "privacy.py").read_text(encoding="utf-8")
        self.assertNotIn("bytes.fromhex", source)
        self.assertNotIn("BLOCKED_TERMS", source)

    def test_readme_uses_final_first_timer_story(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("December 2024", text)
        self.assertNotIn("calendar-order flags excluded", text)
        self.assertIn("## The Story", text)
        self.assertIn("## See the Experience", text)
        self.assertIn("## Try the Demonstration", text)
        self.assertIn("### Open this first", text)
        self.assertIn("## Choose Your Path", text)
        self.assertIn("UAP is a newer term commonly used alongside UFO.", text)
        self.assertIn(
            "It does not download, publish, or analyze real witness reports.",
            text,
        )
        self.assertIn(
            "Example output generated from synthetic demonstration data.",
            text,
        )

    def test_release_manifest_verifies(self) -> None:
        self.assertEqual(verify_manifest(ROOT), [])


if __name__ == "__main__":
    unittest.main()
