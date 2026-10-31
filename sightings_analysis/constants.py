from __future__ import annotations

REQUIRED_COLUMNS = ("report_id", "occurred_at", "reported_date", "state", "shape")

STATE_CODES = frozenset({
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
})

ALLOWED_SHAPES = frozenset({
    "circle", "disk", "fireball", "formation", "light", "oval", "rectangle",
    "sphere", "triangle", "unknown",
})

TIME_BUCKETS = (
    ("Morning", 6, 12),
    ("Afternoon", 12, 18),
    ("Evening", 18, 22),
    ("Night", 22, 24),
    ("Night", 0, 6),
)

TIME_BUCKET_LEGEND = (
    "Morning 06:00-11:59, Afternoon 12:00-17:59, Evening 18:00-21:59, "
    "Night 22:00-05:59 (unequal spans)"
)


def time_of_day(hour: int) -> str:
    """Map a clock hour to its time-of-day category using TIME_BUCKETS."""
    for label, start, end in TIME_BUCKETS:
        if start <= hour < end:
            return label
    raise ValueError(f"hour out of range: {hour}")

SENSITIVE_COLUMN_NAMES = frozenset({
    "address", "email", "full_name", "name", "phone", "street_address",
    "witness_name", "exact_location", "latitude", "longitude",
    "summary", "description", "narrative", "link", "url",
})
