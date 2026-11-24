"""Repository-wide secret-pattern scanner.

Security rule: this script never prints the text that matched a rule. Findings
contain only a relative path, line number and rule id, so a real secret can
never be echoed into CI logs.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".turbo",
    ".output",
    ".parcel-cache",
    ".svelte-kit",
    "dist",
    "build",
    "target",
}

TEXT_SUFFIXES = {
    ".cfg",
    ".env",
    ".example",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".key",
    ".pem",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}

EXCLUDED_SUFFIXES = {".lock", ".log", ".pyc", ".tsbuildinfo"}
TEXT_FILENAMES = {".gitignore", "Dockerfile", "Makefile"}
EXEMPTION_MARKER = "secret-scan-exempt"

_SENSITIVE_NAME = (
    r"(?:SECRET_KEY|API_KEY|ACCESS_KEY|PRIVATE_KEY|CLIENT_SECRET|PASSWORD|PASSWD|PWD|TOKEN)"
)

RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("credentialed-url", re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@]+:[^\s/@]+@")),
    ("private-key-header", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (
        "github-token",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "quoted-secret-assignment",
        re.compile(
            rf"\b{_SENSITIVE_NAME}\b(?:\s*:\s*[A-Za-z_][\w\[\], ]*)?\s*=\s*[rbf]?(['\"])[^'\"]{{6,}}\1",
            re.IGNORECASE,
        ),
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str


def _is_scanned_file(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts[:-1]):
        return False
    name = path.name
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES or name in TEXT_FILENAMES


def scan_repository(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _is_scanned_file(path, root):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if EXEMPTION_MARKER in line:
                continue
            for rule, pattern in RULES:
                if pattern.search(line):
                    findings.append(Finding(str(path.relative_to(root)), line_number, rule))
                    break
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan repository text files for secret patterns.")
    parser.add_argument("root", nargs="?", type=Path, default=ROOT, help="repository root to scan")
    args = parser.parse_args(argv)

    findings = scan_repository(args.root)
    if findings:
        print(f"Secret-pattern findings: {len(findings)}")
        for finding in findings:
            print(f"{finding.path}:{finding.line} [{finding.rule}]")
        print("Matched values are intentionally not printed.")
        return 1
    print("No secret patterns found in repository sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
