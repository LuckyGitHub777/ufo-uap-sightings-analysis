# Data Schema

The v1 pipeline accepts UTF-8 CSV files with five required columns and currently supports U.S. state-coded records.

| Column | Type | Example | Meaning |
|---|---|---|---|
| `report_id` | string | `R-00001` | Unique record identifier |
| `occurred_at` | ISO-8601 date-time | `2024-06-15T21:30` | Local occurrence date and time |
| `reported_date` | ISO-8601 date | `2024-06-16` | Calendar date the record was reported |
| `state` | two-letter code | `CA` | U.S. state or District of Columbia |
| `shape` | controlled text | `triangle` | Reported shape category |

Supported shape values are `circle`, `disk`, `fireball`, `formation`, `light`, `oval`, `rectangle`, `sphere`, `triangle`, and `unknown`.

Full state names such as `California` are not accepted in v1. Convert them to two-letter codes before validation.

Create a template and plain-language field guide:

```bash
python -m sightings_analysis template --output my-reports-template.csv
```

The v1 analysis intentionally does not accept free-text, contact, exact-coordinate, or direct-link columns. This keeps the default workflow focused on aggregate quantitative analysis and reduces public-boundary risk.

## Validation Behavior

- Missing required columns are blocking errors.
- A CSV with headers but no rows is a blocking error.
- Duplicate report identifiers are blocking errors.
- Invalid dates and state codes are blocking errors.
- Unrecognized shapes are warnings and are grouped as `unknown`.
- A report date preceding the occurrence calendar date is a material warning.
- Fewer than two observed months creates an advisory; descriptive analysis still runs and monthly statistics are marked `not_calculated`.
- The source file is never modified.
