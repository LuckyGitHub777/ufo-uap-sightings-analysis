from __future__ import annotations

import csv
from pathlib import Path


TEMPLATE_FIELDS = ["report_id", "occurred_at", "reported_date", "state", "shape"]


def write_template(path: Path) -> tuple[Path, Path]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "report_id": "EXAMPLE-001",
                "occurred_at": "2024-06-15T21:30",
                "reported_date": "2024-06-16",
                "state": "CA",
                "shape": "light",
            }
        )

    guide = path.with_name(f"{path.stem}-README.md")
    guide.write_text(
        """# Sighting-Report CSV Template

This v1 workflow supports U.S. records using two-letter state codes.

| Column | Required format | Example |
|---|---|---|
| `report_id` | Unique text identifier | `EXAMPLE-001` |
| `occurred_at` | ISO-8601 local date-time | `2024-06-15T21:30` |
| `reported_date` | ISO-8601 calendar date | `2024-06-16` |
| `state` | Two-letter U.S. state or DC code | `CA` |
| `shape` | Supported category or `unknown` | `light` |

Do not add names, addresses, witness narratives, email addresses, phone numbers, or direct report links.
""",
        encoding="utf-8",
    )
    return path, guide
