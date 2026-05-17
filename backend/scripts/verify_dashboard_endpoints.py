from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DASHBOARD_ENDPOINTS = (
    "/api/v1/health",
    "/api/v1/dashboard/overview",
    "/api/v1/dashboard/lifecycle",
    "/api/v1/dashboard/review",
    "/api/v1/dashboard/dispatch",
    "/api/v1/dashboard/water-emergency",
)


@dataclass(frozen=True)
class EndpointCheckResult:
    path: str
    ok: bool
    status_code: int | None
    response_keys: tuple[str, ...]
    error: str | None = None


def verify_endpoint(base_url: str, path: str, *, timeout: float) -> EndpointCheckResult:
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(url, method="GET", headers={"accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            response_keys = tuple(sorted(payload)) if isinstance(payload, dict) else ()
            return EndpointCheckResult(
                path=path,
                ok=200 <= response.status < 300,
                status_code=response.status,
                response_keys=response_keys,
            )
    except HTTPError as exc:
        return EndpointCheckResult(
            path=path,
            ok=False,
            status_code=exc.code,
            response_keys=(),
            error=str(exc),
        )
    except (OSError, URLError) as exc:
        return EndpointCheckResult(
            path=path,
            ok=False,
            status_code=None,
            response_keys=(),
            error=str(exc),
        )


def verify_dashboard_endpoints(
    *,
    base_url: str,
    timeout: float = 5.0,
) -> tuple[EndpointCheckResult, ...]:
    return tuple(verify_endpoint(base_url, path, timeout=timeout) for path in DASHBOARD_ENDPOINTS)


def serializable_results(results: tuple[EndpointCheckResult, ...]) -> list[dict[str, Any]]:
    return [asdict(result) for result in results]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify local read-only ACS FSM dashboard API endpoints.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    results = verify_dashboard_endpoints(base_url=args.base_url, timeout=args.timeout)
    print(json.dumps(serializable_results(results), indent=2, sort_keys=True))
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
