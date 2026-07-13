# Data

The public repository does not require or redistribute third-party report data.

## Synthetic demonstration

The demo generates 5,000 deterministic synthetic records at runtime and writes them to:

```text
reports/demo/input/synthetic-reports.csv
```

The generated file follows the documented five-column schema and is included in the run manifest.

## Not included

- Scraped report datasets
- Witness narratives
- Personal or identifying fields
- Original course-project extracts
- Third-party datasets with uncertain redistribution rights

Create a safe input template:

```bash
python -m sightings_analysis template --output my-reports-template.csv
```

Validate an authorized dataset before analysis:

```bash
python -m sightings_analysis validate --reports my-reports.csv
```
