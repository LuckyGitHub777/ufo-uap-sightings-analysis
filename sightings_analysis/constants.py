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

SENSITIVE_COLUMN_NAMES = frozenset({
    "address", "email", "full_name", "name", "phone", "street_address",
    "witness_name", "exact_location", "latitude", "longitude",
    "summary", "description", "narrative", "link", "url",
})
