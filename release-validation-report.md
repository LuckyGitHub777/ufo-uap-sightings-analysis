# Release Validation Report

## Artifact

- Project: `ufo-uap-sightings-analysis`
- Candidate version: `1.0.1`
- Baseline commit: `9ef793f3cb743ac220ce930253a2e1491e9357b3`
- Prepared commit: `recorded in GitHub pull-request evidence after commit creation`
- Validation environment: `Python 3.13.5`
- Discovered automated tests: `29`
- Disposition: local candidate prepared; hosted pull-request, Codespaces, and final release gates remain required

## Purpose of This Patch

Version 1.0.1 closes the public narrative, first-use comprehension, record-use explanation, statistical interpretation, contribution, security-reporting, workflow-maintenance, and release-evidence gaps identified after the initial public release.

It does not add new research claims or expand the analytical scope.

## Local Product and UX Verification

| Control | Result |
|---|---|
| Natural README story | Passed static review: identity → story → visual preview → safe demonstration → first result → deeper use → evidence |
| Unnecessary project-history date detail | Removed |
| First visual | Subject-matter shape figure with visible synthetic-data caption |
| First result to open | Explicitly identified |
| Layperson demonstration guidance | Codespaces terminal location and five-step outcome explained |
| Curated example gallery | Added with first-result, figure, record-accounting, and evidence guidance |
| Public experience contract | Added and linked from release controls |
| Evidence-status panel | Added to the README |
| Local clone-to-demo path | Documented |
| Codespaces badge | Added; live launch remains a manual hosted gate |
| Prepared-CSV limitation | Explicit |
| Record-use figure | Plain language |
| Reporting-delay exclusion | Explained as analysis-specific |
| Plain-language statistical interpretation | Generated |
| Generated summary hierarchy | Overview and meaning precede detailed statistics |
| Visual system | Restrained high-contrast palette applied to generated SVGs |
| Statistical glossary | Generated |
| Contribution path | Privacy-safe templates included |
| Security path | Direct private-reporting route documented |
| Personal and course artifacts | Excluded |

## Local Engineering Verification

| Control | Result |
|---|---|
| Automated tests | Passed |
| Deterministic demo comparison | Passed |
| Privacy scan | Passed |
| Release manifest | Passed |
| Installed-wheel execution outside repository | Passed |
| Input immutability and output protection | Covered by tests |
| Python source compilation | Passed |
| Markdown relative links | Passed |
| Generated summary and SVG line-break integrity | Passed |
| SVG XML parsing | Passed |
| ZIP path safety and duplicate entries | Passed |
| Git diff whitespace check | Passed |

## Workflow Controls

- `actions/checkout` pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`)
- `actions/setup-python` pinned to `5fda3b95a4ea91299a34e894583c3862153e4b97` (`v7.0.0`)
- Checkout credentials are not persisted
- Workflow token permissions remain read-only
- Python 3.11, 3.12, and 3.13 tests remain configured
- Ubuntu, Windows, and macOS portability jobs remain configured
- Installed-wheel smoke verification is added
- Monthly GitHub Actions Dependabot updates are configured

## Public Boundary

The repository must continue to exclude:

- raw third-party report data,
- witness narratives,
- original course submissions and course materials,
- personal biography and contact details,
- credentials and local user paths,
- restricted datasets,
- unsupported military, nuclear, causal, or event-verification findings.

## Hosted Gates Still Required

The local validation does not establish these hosted results:

1. Push the exact prepared commit to one review branch.
2. Open one pull request.
3. Confirm every hosted CI and Public Boundary job passes.
4. Review the rendered README and SVGs on desktop and mobile.
5. Launch Codespaces from the badge and run the demo.
6. Enable Issues only after the privacy-safe templates are present.
7. Enable private vulnerability reporting and confirm the direct route works.
8. Merge only the exact reviewed pull-request head.
9. Rebuild the final release ZIP from the merge commit.
10. Tag and publish `v1.0.1`, then perform a signed-out readback.

## Final Boundary

The `v1.0.0` tag, release, and asset remain unchanged. Version `1.0.1` is a focused human-comprehension and maintenance patch.
