from __future__ import annotations

import csv
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

DEFAULT_SEED = 20241205
DEFAULT_ROWS = 5000

STATES = (
    ("CA", 16), ("TX", 13), ("FL", 11), ("NY", 9), ("PA", 7),
    ("WA", 7), ("AZ", 6), ("OH", 6), ("NC", 6), ("CO", 5),
    ("OR", 5), ("IL", 5), ("MI", 4), ("NJ", 4), ("GA", 4),
    ("VA", 4), ("NV", 3), ("NM", 3), ("MA", 3), ("MN", 3),
)

SHAPES = (
    ("light", 27), ("circle", 15), ("triangle", 12), ("fireball", 10),
    ("sphere", 9), ("disk", 8), ("formation", 7), ("oval", 5),
    ("rectangle", 3), ("unknown", 4),
)


def _weighted_choice(rng: random.Random, items: tuple[tuple[str, int], ...]) -> str:
    values = [item[0] for item in items]
    weights = [item[1] for item in items]
    return rng.choices(values, weights=weights, k=1)[0]


def generate_rows(*, rows: int = DEFAULT_ROWS, seed: int = DEFAULT_SEED) -> list[dict[str, str]]:
    rng = random.Random(seed)
    start = date(2020, 1, 1)
    end = date(2024, 12, 31)
    span = (end - start).days
    output: list[dict[str, str]] = []

    for index in range(rows):
        if index == 0:
            occurred_date = start
        elif index == rows - 1:
            occurred_date = end
        else:
            occurred_date = start + timedelta(days=rng.randint(0, span))

        hour = rng.choices(
            population=list(range(24)),
            weights=[2, 2, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 7, 10, 13, 15, 14, 10, 6],
            k=1,
        )[0]
        occurred_at = datetime.combine(
            occurred_date,
            time(hour=hour, minute=rng.choice([0, 5, 10, 15, 20, 30, 40, 45, 50, 55])),
        )

        # Exactly 34 intentionally invalid calendar-order records support validation UX.
        if index < 34:
            reported_date = occurred_date - timedelta(days=1 + index % 3)
        elif index < 234:
            reported_date = occurred_date + timedelta(days=30 + index % 91)
        elif index < 2834:
            reported_date = occurred_date
        else:
            reported_date = occurred_date + timedelta(days=1 + index % 14)

        output.append({
            "report_id": f"SYN-{index + 1:05d}",
            "occurred_at": occurred_at.isoformat(timespec="minutes"),
            "reported_date": reported_date.isoformat(),
            "state": _weighted_choice(rng, STATES),
            "shape": _weighted_choice(rng, SHAPES),
        })
    return output


def write_csv(path: Path, *, rows: int = DEFAULT_ROWS, seed: int = DEFAULT_SEED) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = generate_rows(rows=rows, seed=seed)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["report_id", "occurred_at", "reported_date", "state", "shape"])
        writer.writeheader()
        writer.writerows(records)
    return path
