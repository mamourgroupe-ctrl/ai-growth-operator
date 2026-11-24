"""Phase 1 remediation (#32): tests for the repository secret scanner."""

from pathlib import Path

from scripts.check_no_secrets import EXEMPTION_MARKER, ROOT, Finding, main, scan_repository


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
    return path


def _quoted_assignment(name: str, value: str) -> str:
    # Split literals so this test file itself never contains a scannable secret.
    return name + " = " + '"' + value + '"'


def test_detects_quoted_secret_without_printing_value(tmp_path: Path, capsys) -> None:
    secret = "abc123def456ghi"
    _write(tmp_path / "leak.py", _quoted_assignment("SECRET" + "_KEY", secret))

    findings = scan_repository(tmp_path)
    assert findings == [Finding("leak.py", 1, "quoted-secret-assignment")]
    assert secret not in repr(findings)

    assert main([str(tmp_path)]) == 1
    output = capsys.readouterr().out
    assert "leak.py:1 [quoted-secret-assignment]" in output
    assert secret not in output


def test_detects_credentialed_url_key_and_tokens(tmp_path: Path) -> None:
    _write(tmp_path / "config.yml", "url: " + "postgres" + "ql" + "://user:password@host/db")
    _write(tmp_path / "key.pem", "-----BEGIN " + "RSA PRIVATE KEY-----")
    _write(tmp_path / "aws.py", "key = " + '"' + "AKIA" + "ABCDEFGHIJKLMNOP" + '"')
    _write(tmp_path / "github.py", "token = " + '"' + "ghp_" + "a" * 36 + '"')

    rules = {finding.rule for finding in scan_repository(tmp_path)}
    assert rules == {
        "credentialed-url",
        "private-key-header",
        "aws-access-key-id",
        "github-token",
    }


def test_exemption_marker_suppresses_dummy_value(tmp_path: Path) -> None:
    line = _quoted_assignment("PASSWORD", "dummydummyvalue") + f"  # {EXEMPTION_MARKER}: dummy test credential"
    _write(tmp_path / "tests.py", line)
    assert scan_repository(tmp_path) == []


def test_excluded_paths_are_not_scanned_but_env_example_is(tmp_path: Path) -> None:
    _write(tmp_path / ".venv" / "lib" / "leak.py", _quoted_assignment("SECRET_KEY", "venvvalue123"))
    _write(tmp_path / "node_modules" / "leak.js", _quoted_assignment("API_KEY", "nodevalue123"))
    _write(tmp_path / ".env", _quoted_assignment("SECRET_KEY", "realvalue123"))
    _write(tmp_path / "app.pyc", _quoted_assignment("SECRET_KEY", "pycvalue123"))
    assert scan_repository(tmp_path) == []

    _write(tmp_path / ".env.example", _quoted_assignment("SECRET_KEY", "examplevalue123"))
    assert [finding.rule for finding in scan_repository(tmp_path)] == ["quoted-secret-assignment"]


def test_current_repository_has_no_findings() -> None:
    assert scan_repository(ROOT) == []
