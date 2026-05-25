from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

BACKEND_AUTH_PLACEHOLDERS = {
    "ACS_FSM_AUTH_PROVIDER": "disabled",
    "ACS_FSM_AUTH_ENABLED": "false",
    "ACS_FSM_AUTH_ISSUER_URL": "",
    "ACS_FSM_AUTH_AUDIENCE": "",
    "ACS_FSM_AUTH_JWKS_URL": "",
    "ACS_FSM_AUTH_ALLOWED_EMAIL_DOMAINS": "",
    "ACS_FSM_AUTH_REQUIRE_VERIFIED_EMAIL": "true",
    "ACS_FSM_AUTH_LOCAL_DEV_MODE": "false",
    "ACS_FSM_AUTH_ROLE_CLAIM": "",
    "ACS_FSM_AUTH_PERMISSION_CLAIM": "",
}
FRONTEND_AUTH_PLACEHOLDERS = {
    "NEXT_PUBLIC_ACS_AUTH_ENABLED": "false",
    "NEXT_PUBLIC_ACS_AUTH_PROVIDER": "disabled",
    "NEXT_PUBLIC_ACS_AUTH_LOGIN_URL": "",
    "NEXT_PUBLIC_ACS_AUTH_LOGOUT_URL": "",
    "NEXT_PUBLIC_ACS_AUTH_STATUS_URL": "",
}
EXAMPLE_PLACEHOLDER_EXPECTATIONS = {
    ".env.example": BACKEND_AUTH_PLACEHOLDERS,
    "backend/.env.example": BACKEND_AUTH_PLACEHOLDERS,
    "frontend/.env.example": FRONTEND_AUTH_PLACEHOLDERS,
}
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_KEY_PATTERNS = tuple(
    "-" * 5 + marker + "-" * 5
    for marker in (
        "BEGIN " + "PRIVATE KEY",
        "BEGIN RSA " + "PRIVATE KEY",
        "BEGIN EC " + "PRIVATE KEY",
        "BEGIN OPENSSH " + "PRIVATE KEY",
    )
)
OBVIOUS_TOKEN_PATTERNS = (
    "sk" + "-proj-" + r"[A-Za-z0-9_-]{20,}",
    "sk" + "-" + r"[A-Za-z0-9_-]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"AIza[0-9A-Za-z_-]{20,}",
    r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}",
)
OBVIOUS_TOKEN_PATTERN = re.compile("(" + "|".join(OBVIOUS_TOKEN_PATTERNS) + ")")


@dataclass(frozen=True)
class AuthConfigSafetyFinding:
    key: str
    severity: str
    path: str
    detail: str


@dataclass(frozen=True)
class AuthConfigSafetyReport:
    ok: bool
    checked_files: tuple[str, ...]
    findings: tuple[AuthConfigSafetyFinding, ...]
    placeholder_values_only: bool
    env_file_tracked: bool
    env_local_file_tracked: bool
    service_account_json_tracked: bool
    private_key_detected: bool
    obvious_token_detected: bool
    missing_safe_placeholder_defaults: tuple[str, ...]


def tracked_files_from_git(repo_root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=False,
    )
    return tuple(path.decode("utf-8") for path in result.stdout.split(b"\0") if path)


def serialize_report(report: AuthConfigSafetyReport) -> dict[str, object]:
    return asdict(report)


def run_auth_config_safety_checks(
    repo_root: Path,
    *,
    tracked_files: tuple[str, ...] | None = None,
) -> AuthConfigSafetyReport:
    repo_root = repo_root.resolve()
    source_files = tracked_files
    if source_files is None:
        source_files = tracked_files_from_git(repo_root)
    tracked = tuple(sorted(source_files))
    findings: list[AuthConfigSafetyFinding] = []
    missing_placeholders: list[str] = []
    service_account_json_tracked = False
    private_key_detected = False
    obvious_token_detected = False

    env_file_tracked = any(Path(path).name == ".env" for path in tracked)
    env_local_file_tracked = any(Path(path).name == ".env.local" for path in tracked)
    if env_file_tracked:
        findings.append(
            AuthConfigSafetyFinding(
                key="tracked_env_file",
                severity="error",
                path=".env",
                detail="A tracked .env file is not allowed.",
            ),
        )
    if env_local_file_tracked:
        findings.append(
            AuthConfigSafetyFinding(
                key="tracked_env_local_file",
                severity="error",
                path=".env.local",
                detail="A tracked .env.local file is not allowed.",
            ),
        )

    for relative_path in tracked:
        path = Path(relative_path)
        if path.name in {".env", ".env.local"}:
            continue
        full_path = repo_root / path
        text = _read_text_sample(full_path)
        if text is None:
            continue

        looks_like_service_account = path.suffix == ".json" and (
            "service-account" in path.name.lower()
            or "service_account" in path.name.lower()
            or '"type": "service_account"' in text
        )
        if looks_like_service_account:
            service_account_json_tracked = True
            findings.append(
                AuthConfigSafetyFinding(
                    key="tracked_service_account_json",
                    severity="error",
                    path=relative_path,
                    detail="Tracked service account JSON is not allowed.",
                ),
            )

        if any(pattern in text for pattern in PRIVATE_KEY_PATTERNS):
            private_key_detected = True
            findings.append(
                AuthConfigSafetyFinding(
                    key="private_key_detected",
                    severity="error",
                    path=relative_path,
                    detail="Private key material detected; value redacted.",
                ),
            )

        if OBVIOUS_TOKEN_PATTERN.search(text):
            obvious_token_detected = True
            findings.append(
                AuthConfigSafetyFinding(
                    key="obvious_token_detected",
                    severity="error",
                    path=relative_path,
                    detail="Obvious token-like value detected; value redacted.",
                ),
            )

        expected_placeholders = EXAMPLE_PLACEHOLDER_EXPECTATIONS.get(relative_path)
        if expected_placeholders is not None:
            parsed = _parse_env_example(text)
            for name, expected_value in expected_placeholders.items():
                if name not in parsed:
                    missing_placeholders.append(f"{relative_path}:{name}")
                    findings.append(
                        AuthConfigSafetyFinding(
                            key="missing_safe_placeholder_default",
                            severity="error",
                            path=relative_path,
                            detail=f"Missing safe placeholder for {name}.",
                        ),
                    )
                elif parsed[name] != expected_value:
                    findings.append(
                        AuthConfigSafetyFinding(
                            key="unsafe_placeholder_value",
                            severity="error",
                            path=relative_path,
                            detail=f"{name} has a non-placeholder value; value redacted.",
                        ),
                    )

    placeholder_values_only = not any(
        finding.key in {"missing_safe_placeholder_default", "unsafe_placeholder_value"}
        for finding in findings
    )
    return AuthConfigSafetyReport(
        ok=not findings,
        checked_files=tracked,
        findings=tuple(findings),
        placeholder_values_only=placeholder_values_only,
        env_file_tracked=env_file_tracked,
        env_local_file_tracked=env_local_file_tracked,
        service_account_json_tracked=service_account_json_tracked,
        private_key_detected=private_key_detected,
        obvious_token_detected=obvious_token_detected,
        missing_safe_placeholder_defaults=tuple(missing_placeholders),
    )


def _read_text_sample(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:200_000]
    except OSError:
        return None


def _parse_env_example(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        parsed[name.strip()] = value.strip().strip('"').strip("'")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check ACS-FSM future auth config placeholders without printing secrets.",
    )
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    report = run_auth_config_safety_checks(Path(args.repo_root))
    payload = serialize_report(report)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        status = "ok" if report.ok else "failed"
        print(f"auth_config_safety={status}")
        for finding in report.findings:
            print(f"{finding.severity}: {finding.path}: {finding.detail}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
