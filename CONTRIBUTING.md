# Contributing

Contributions should improve usability, validation, statistical transparency, tests, documentation, portability, or responsible interpretation.

## Before Opening a Pull Request

```bash
python -m unittest discover -s tests -v
python -m sightings_analysis privacy-scan .
```

If the pull request intentionally changes release files, regenerate and verify the manifest:

```bash
python -m sightings_analysis build-release-manifest --force
python -m sightings_analysis verify-release
```

Do not submit raw third-party reports, witness narratives, personal data, credentials, restricted datasets, or files whose redistribution rights are uncertain.

The public scanner checks generic patterns. Maintainers may additionally run a private denylist stored outside the repository through the `SIGHTINGS_PRIVATE_DENYLIST_FILE` environment variable.
