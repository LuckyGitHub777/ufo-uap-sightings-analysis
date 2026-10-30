# Contributing

Contributions should improve usability, validation, statistical transparency, tests, documentation, portability, or responsible interpretation.

## Public Feedback

Public issues are intended for reproducible software or documentation defects and bounded feature proposals. Never attach real sighting reports, witness narratives, personal data, credentials, private infrastructure details, restricted datasets, or files whose redistribution rights are uncertain.

Use the repository issue forms when Issues are enabled. Provide a minimal synthetic reproduction whenever possible.

Security concerns must follow [`SECURITY.md`](SECURITY.md) and must not be disclosed through a public issue or pull request.

## Before Opening a Pull Request

```bash
python -m unittest discover -s tests -v
python -m sightings_analysis privacy-scan .
```

If the pull request intentionally changes controlled release files, regenerate and verify the manifest:

```bash
python -m sightings_analysis build-release-manifest --force
python -m sightings_analysis verify-release
```

Keep pull requests focused. Explain the user problem, the change, the validation performed, and any remaining limitation.

The public scanner checks generic patterns. Maintainers may additionally run a private denylist stored outside the repository through the `SIGHTINGS_PRIVATE_DENYLIST_FILE` environment variable.
