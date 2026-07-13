from __future__ import annotations

import csv
import os
import re
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".py", ".toml", ".yml", ".yaml", ".json", ".csv", ".html"}
SKIP_PARTS = {".git", "__pycache__", "build", "dist", ".pytest_cache", ".venv", ".tox"}
PROHIBITED_DATA_COLUMNS = {
    "address",
    "email",
    "full_name",
    "name",
    "phone",
    "summary",
    "description",
    "narrative",
    "witness_name",
    "link",
    "url",
}
PROHIBITED_RELEASE_NAMES = {".env", "id_rsa", "id_ed25519"}
PROHIBITED_PATHS = {
    "data/raw",
    "data/scraped",
    "docs/original-submission",
    "original-submission",
}

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?1[-. ]?)?(?:\(\d{3}\)[-. ]?|\d{3}[-. ])\d{3}[-. ]\d{4}(?!\w)")
LOCAL_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\Users\\[^\\\s]+|/Users/[^/\s]+|/home/[^/\s]+)")
CREDENTIAL_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)


def _private_terms() -> tuple[str, ...]:
    """Load optional private release terms from a file outside the repository."""

    denylist_path = os.environ.get("SIGHTINGS_PRIVATE_DENYLIST_FILE")
    if not denylist_path:
        return ()
    path = Path(denylist_path).expanduser()
    if not path.is_file():
        return ()
    return tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    private_terms = tuple(term.lower() for term in _private_terms())
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        relative_text = relative.as_posix()
        if set(relative.parts) & SKIP_PARTS:
            continue
        if path.name in PROHIBITED_RELEASE_NAMES:
            findings.append(f"prohibited release file: {relative_text}")
        if any(relative_text == item or relative_text.startswith(f"{item}/") for item in PROHIBITED_PATHS):
            findings.append(f"prohibited release path: {relative_text}")
        if path.name == "RELEASE_MANIFEST.json":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"unexpected non-UTF-8 text file: {relative_text}")
            continue
        scanner_source = relative_text == "sightings_analysis/privacy.py"
        if not scanner_source and EMAIL_PATTERN.search(text):
            findings.append(f"email-like value: {relative_text}")
        if not scanner_source and PHONE_PATTERN.search(text):
            findings.append(f"phone-like value: {relative_text}")
        if not scanner_source and LOCAL_PATH_PATTERN.search(text):
            findings.append(f"local user path: {relative_text}")
        if not scanner_source and CREDENTIAL_PATTERN.search(text):
            findings.append(f"credential-like value: {relative_text}")
        lowered = text.lower()
        if private_terms and any(term in lowered for term in private_terms):
            findings.append(f"private release term: {relative_text}")
        if path.suffix.lower() == ".csv":
            try:
                with path.open(newline="", encoding="utf-8-sig") as handle:
                    header = next(csv.reader(handle), [])
            except csv.Error:
                header = []
            prohibited = sorted(
                {value.strip().lower() for value in header} & PROHIBITED_DATA_COLUMNS
            )
            if prohibited:
                findings.append(
                    f"prohibited CSV columns in {relative_text}: {', '.join(prohibited)}"
                )
    return findings
