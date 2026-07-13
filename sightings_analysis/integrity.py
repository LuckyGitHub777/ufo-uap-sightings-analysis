from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".venv",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_PREFIXES = {("reports", "demo")}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _excluded(relative: Path) -> bool:
    if set(relative.parts) & EXCLUDED_PARTS or relative.suffix in EXCLUDED_SUFFIXES:
        return True
    if any(part.endswith(".egg-info") for part in relative.parts):
        return True
    return any(relative.parts[: len(prefix)] == prefix for prefix in EXCLUDED_PREFIXES)


def build_manifest(root: Path) -> dict[str, object]:
    files: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.name == "RELEASE_MANIFEST.json" or _excluded(relative):
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return {
        "format": "ufo-uap-sightings-analysis-release-manifest-v1",
        "file_count": len(files),
        "files": files,
    }


def write_manifest(root: Path) -> Path:
    path = root / "RELEASE_MANIFEST.json"
    payload = json.dumps(build_manifest(root), indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    return path


def verify_manifest(root: Path) -> list[str]:
    path = root / "RELEASE_MANIFEST.json"
    if not path.exists():
        return ["RELEASE_MANIFEST.json is missing"]
    expected = json.loads(path.read_text(encoding="utf-8"))
    actual = build_manifest(root)
    findings: list[str] = []
    if expected.get("format") != actual.get("format"):
        findings.append("manifest format differs")
    expected_files = {item["path"]: item for item in expected.get("files", [])}
    actual_files = {item["path"]: item for item in actual.get("files", [])}
    for missing in sorted(set(expected_files) - set(actual_files)):
        findings.append(f"missing file: {missing}")
    for extra in sorted(set(actual_files) - set(expected_files)):
        findings.append(f"untracked release file: {extra}")
    for name in sorted(set(expected_files) & set(actual_files)):
        if expected_files[name]["sha256"] != actual_files[name]["sha256"]:
            findings.append(f"hash mismatch: {name}")
        if expected_files[name]["size_bytes"] != actual_files[name]["size_bytes"]:
            findings.append(f"size mismatch: {name}")
    return findings
