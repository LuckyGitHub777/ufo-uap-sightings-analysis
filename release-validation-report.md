# Release Validation Report

## Artifact

- Project: `ufo-uap-sightings-analysis`
- Version: `1.0.0`
- Release type: first public release candidate
- Validation environment: Linux, Python 3.13.5

## Product-Correctness Verification

The release candidate was tested against the defects identified during V&V.

| Control | Result |
|---|---|
| Synthetic versus user-data labels | Passed across Markdown, JSON, CSV, SVG, sample-flow, and completion output |
| Empty dataset | Blocked with an actionable message and no traceback |
| One-row or one-month dataset | Descriptive output generated; monthly statistics marked `not_calculated` |
| Missing calendar month | Preserved as a zero-report month in the monthly series |
| Installed demo input | Generated under the selected output directory |
| Installed package directory | No application data directory created; Python source hashes unchanged |
| Source input | Read without modification |
| Existing output | Protected unless `--force` is supplied |
| Paths containing spaces | Passed |
| Deterministic demo | Repeated outputs matched byte for byte in the same environment |

## Public-Boundary Verification

- No raw third-party report data
- No witness narratives
- No original course submission files
- No personal biography, contact details, local user paths, or credentials
- No encoded user-specific denylist table in the public scanner
- Generic public scan passed
- Optional external private-denylist scan passed
- Human review remains required before publication

## UX Verification

- `--help` lists all end-user commands
- `demo` completes with one command
- `template` creates a CSV and field guide
- `validate` is human-readable by default
- `validate --json` provides machine-readable output
- Warning output is summarized with limited examples
- Exact statistical period boundaries appear in reports
- State and shape figures are generated
- Every material sample change is disclosed

## Engineering Verification

- Standard-library-only runtime
- Offline application behavior
- Automated unit and integration tests
- GitHub Actions for Python 3.11, 3.12, and 3.13 on Linux
- Portability smoke-test workflow for Linux, Windows, and macOS
- Codespaces development-container configuration
- Deterministic release-manifest generation and verification

## Archive Evidence

The final ZIP is validated after packaging from a fresh extraction. Its SHA-256 is recorded in the companion validation artifact distributed alongside the ZIP, because an archive cannot reliably contain its own final hash.

## Remaining Live-GitHub Checks

The following checks require the repository to exist on GitHub and cannot be completed from a local release archive:

- Confirm hosted GitHub Actions runs
- Confirm live Codespaces launch
- Add a repository-specific one-click Codespaces badge after the owner URL is known
- Confirm the first public commit begins from the release-clean directory
