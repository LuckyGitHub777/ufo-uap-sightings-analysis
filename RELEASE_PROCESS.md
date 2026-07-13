# Release Process

This document describes the repeatable release workflow. Completed evidence for the current artifact is recorded in [`release-validation-report.md`](release-validation-report.md).

## 1. Start From a Release-Clean Directory

Create the public repository from a new directory and clean Git history that never contained raw third-party data, witness narratives, course submissions, personal logs, or private denylist values.

## 2. Run Product Tests

```bash
python -m unittest discover -s tests -v
```

## 3. Run Public-Boundary Review

```bash
python -m sightings_analysis privacy-scan .
```

A private maintainer denylist may be supplied from outside the repository:

```bash
SIGHTINGS_PRIVATE_DENYLIST_FILE=/path/outside/repo/denylist.txt \
python -m sightings_analysis privacy-scan .
```

Automated scanning supports but does not replace human review.

## 4. Regenerate the Release Manifest

```bash
python -m sightings_analysis build-release-manifest --force
python -m sightings_analysis verify-release
```

The manifest is deterministic and excludes generated `reports/demo/`, build files, caches, virtual environments, and the manifest itself.

## 5. Validate the User Experience

From a fresh extraction or clone:

```bash
python -m sightings_analysis --help
python -m sightings_analysis template --output template.csv
python -m sightings_analysis demo --output reports/demo
python -m sightings_analysis validate --reports template.csv
```

Also verify:

- a zero-row CSV fails with an actionable message,
- a one-month CSV produces descriptive outputs and marks monthly statistics not calculated,
- a dataset with a missing middle month retains that month as zero,
- user-supplied outputs never say synthetic,
- the source input hash does not change,
- existing output requires `--force`,
- paths containing spaces work.

## 6. Validate the Installed Package

Build and install the wheel into a clean environment, change to a directory outside the source tree, and run the demo. Confirm that the generated input is written under the selected output directory and that the installed package directory remains unchanged.

## 7. Package and Inspect the ZIP

Confirm:

- no unsafe paths,
- no duplicate entries,
- no `.git`, cache, build, or environment directories,
- no raw or restricted data,
- no broken Markdown links,
- deterministic demo outputs match on repeated runs.

## 8. Record Evidence

Update `release-validation-report.md` with the artifact hash, environment, commands, results, known limits, and final decision.
