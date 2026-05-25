from __future__ import annotations

import json
from pathlib import Path

from scripts.check_auth_config_safety import run_auth_config_safety_checks, serialize_report

TOKEN_SENTINEL = "sk" + "-proj" + "-" + ("a" * 40)
PRIVATE_KEY_BEGIN_SENTINEL = "-" * 5 + "BEGIN " + "PRIVATE KEY" + "-" * 5
PRIVATE_KEY_END_SENTINEL = "-" * 5 + "END " + "PRIVATE KEY" + "-" * 5

ROOT_ENV_EXAMPLE = """# safe root example
ACS_FSM_AUTH_PROVIDER=disabled
ACS_FSM_AUTH_ENABLED=false
ACS_FSM_AUTH_ISSUER_URL=
ACS_FSM_AUTH_AUDIENCE=
ACS_FSM_AUTH_JWKS_URL=
ACS_FSM_AUTH_ALLOWED_EMAIL_DOMAINS=
ACS_FSM_AUTH_REQUIRE_VERIFIED_EMAIL=true
ACS_FSM_AUTH_LOCAL_DEV_MODE=false
ACS_FSM_AUTH_ROLE_CLAIM=
ACS_FSM_AUTH_PERMISSION_CLAIM=
"""

FRONTEND_ENV_EXAMPLE = """# safe frontend example
NEXT_PUBLIC_ACS_AUTH_ENABLED=false
NEXT_PUBLIC_ACS_AUTH_PROVIDER=disabled
NEXT_PUBLIC_ACS_AUTH_LOGIN_URL=
NEXT_PUBLIC_ACS_AUTH_LOGOUT_URL=
NEXT_PUBLIC_ACS_AUTH_STATUS_URL=
"""


def write_safe_examples(repo_root):
    (repo_root / ".env.example").write_text(ROOT_ENV_EXAMPLE, encoding="utf-8")
    backend = repo_root / "backend"
    frontend = repo_root / "frontend"
    backend.mkdir()
    frontend.mkdir()
    (backend / ".env.example").write_text(ROOT_ENV_EXAMPLE, encoding="utf-8")
    (frontend / ".env.example").write_text(FRONTEND_ENV_EXAMPLE, encoding="utf-8")


def test_auth_config_safety_check_accepts_safe_placeholders(tmp_path) -> None:
    write_safe_examples(tmp_path)

    report = run_auth_config_safety_checks(
        tmp_path,
        tracked_files=(
            ".env.example",
            "backend/.env.example",
            "frontend/.env.example",
        ),
    )

    assert report.ok is True
    assert report.placeholder_values_only is True
    assert report.env_file_tracked is False
    assert report.env_local_file_tracked is False
    assert report.service_account_json_tracked is False
    assert report.private_key_detected is False
    assert report.obvious_token_detected is False
    assert report.missing_safe_placeholder_defaults == ()
    assert report.findings == ()


def test_auth_config_safety_check_redacts_secret_values(tmp_path) -> None:
    write_safe_examples(tmp_path)
    (tmp_path / "backend" / ".env.example").write_text(
        ROOT_ENV_EXAMPLE.replace(
            "ACS_FSM_AUTH_ISSUER_URL=",
            f"ACS_FSM_AUTH_ISSUER_URL={TOKEN_SENTINEL}",
        ),
        encoding="utf-8",
    )
    service_account = (
        '{"type": "service_account", "private_key": "'
        + PRIVATE_KEY_BEGIN_SENTINEL
        + "\\nsecret\\n"
        + PRIVATE_KEY_END_SENTINEL
        + '"}'
    )
    (tmp_path / "service-account.json").write_text(
        service_account,
        encoding="utf-8",
    )

    report = run_auth_config_safety_checks(
        tmp_path,
        tracked_files=(
            ".env.example",
            "backend/.env.example",
            "frontend/.env.example",
            "service-account.json",
        ),
    )
    payload = json.dumps(serialize_report(report), sort_keys=True)

    assert report.ok is False
    assert report.placeholder_values_only is False
    assert report.service_account_json_tracked is True
    assert report.private_key_detected is True
    assert report.obvious_token_detected is True
    assert "unsafe_placeholder_value" in {finding.key for finding in report.findings}
    assert TOKEN_SENTINEL not in payload
    assert PRIVATE_KEY_BEGIN_SENTINEL not in payload


def test_auth_config_safety_check_does_not_flag_own_constructed_patterns(
    tmp_path,
) -> None:
    write_safe_examples(tmp_path)
    repo_backend = Path(__file__).resolve().parents[1]
    script_source = repo_backend / "scripts" / "check_auth_config_safety.py"
    test_source = Path(__file__).resolve()
    helper_copy = tmp_path / "backend" / "scripts" / "check_auth_config_safety.py"
    test_copy = tmp_path / "backend" / "tests" / "test_auth_config_safety.py"
    helper_copy.parent.mkdir(parents=True)
    test_copy.parent.mkdir(parents=True)
    helper_copy.write_text(script_source.read_text(encoding="utf-8"), encoding="utf-8")
    test_copy.write_text(test_source.read_text(encoding="utf-8"), encoding="utf-8")

    fake_secret_path = tmp_path / "backend" / "fake-secret.txt"
    fake_secret_path.write_text(
        "\n".join(
            (
                TOKEN_SENTINEL,
                PRIVATE_KEY_BEGIN_SENTINEL,
                "synthetic test body",
                PRIVATE_KEY_END_SENTINEL,
            ),
        ),
        encoding="utf-8",
    )

    report = run_auth_config_safety_checks(
        tmp_path,
        tracked_files=(
            ".env.example",
            "backend/.env.example",
            "frontend/.env.example",
            "backend/scripts/check_auth_config_safety.py",
            "backend/tests/test_auth_config_safety.py",
            "backend/fake-secret.txt",
        ),
    )
    finding_paths = {finding.path for finding in report.findings}
    payload = json.dumps(serialize_report(report), sort_keys=True)

    assert report.ok is False
    assert "backend/scripts/check_auth_config_safety.py" not in finding_paths
    assert "backend/tests/test_auth_config_safety.py" not in finding_paths
    assert "backend/fake-secret.txt" in finding_paths
    assert report.private_key_detected is True
    assert report.obvious_token_detected is True
    assert TOKEN_SENTINEL not in payload
    assert PRIVATE_KEY_BEGIN_SENTINEL not in payload
