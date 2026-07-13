# Bring Your Own Data

Use only data you are authorized to access and analyze.

The v1 workflow supports U.S. records prepared to the documented five-column schema.

## 1. Create a Template

```bash
python -m sightings_analysis template \
  --output my-reports-template.csv
```

This creates both a CSV and a short field guide.

## 2. Validate

```bash
python -m sightings_analysis validate \
  --reports my-reports.csv
```

The default output is written for people: record counts, date coverage, warning totals, examples, and a suggested next command.

For complete machine-readable output:

```bash
python -m sightings_analysis validate \
  --reports my-reports.csv \
  --json
```

To save the full JSON report while keeping the human summary:

```bash
python -m sightings_analysis validate \
  --reports my-reports.csv \
  --output reports/validation/data-quality-report.json
```

Validation checks schema errors, date problems, duplicate identifiers, unsupported geography, quality warnings, and disallowed sensitive columns. It does not modify the source file.

Large warning sets are summarized in the terminal. The complete JSON report retains all row-level findings.

## 3. Analyze

```bash
python -m sightings_analysis analyze \
  --reports my-reports.csv \
  --output reports/my-analysis
```

If material warnings exist, review them and explicitly continue when appropriate:

```bash
python -m sightings_analysis analyze \
  --reports my-reports.csv \
  --output reports/my-analysis \
  --allow-warnings
```

A dataset with one observed month still receives descriptive outputs. Monthly statistical calculations are recorded as `not_calculated` rather than raising a traceback.

## 4. Protect Existing Output

The command refuses to replace a nonempty output directory. Use `--force` only after reviewing the existing files.

## Public-Boundary Reminder

The automated scan checks common patterns and prohibited release paths. It cannot guarantee that a dataset contains no personal or sensitive information. Human review remains required before publication.
