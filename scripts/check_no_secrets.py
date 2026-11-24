import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "apps/api/app", ROOT / "apps/web/app"]
EXTENSIONS = {".py", ".ts", ".tsx", ".mjs"}
PATTERN = re.compile(r"\b(SECRET_KEY|API_KEY|PASSWORD)\s*=\s*[\"'][^\"']+[\"']")


def main() -> int:
    findings: list[str] = []
    for directory in SCAN_DIRS:
        for path in directory.rglob("*"):
            if path.suffix not in EXTENSIONS or not path.is_file():
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if PATTERN.search(line):
                    findings.append(f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}")
    if findings:
        print("Hardcoded secret pattern found:")
        print("\n".join(findings))
        return 1
    print("No hardcoded secret patterns in application source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
