"""Healthcheck all workshop services."""

import json
import subprocess
from urllib.error import URLError
from urllib.request import urlopen

from workshop_cli.utils.formatting import FAIL, OK
from workshop_cli.utils.api import API_URL


def _container_running(service: str) -> bool:
    """Return True if the docker compose service container is running."""
    result = subprocess.run(
        ["docker", "compose", "ps", "--status", "running", "--format", "json", service],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() != ""


def _check_api_health() -> tuple[bool, str]:
    """Hit the API /health endpoint and return (ok, detail)."""
    try:
        with urlopen(f"{API_URL}/health", timeout=5) as resp:
            data = json.loads(resp.read())
            if data.get("status") == "ok":
                return True, "status ok"
            return False, f"unexpected response: {data}"
    except URLError as exc:
        return False, str(exc.reason)
    except Exception as exc:
        return False, str(exc)


def cmd_health(args):
    services = ["redis", "postgres", "api", "frontend"]

    print("\nService Health")
    print("─" * 45)

    all_ok = True
    for svc in services:
        running = _container_running(svc)
        mark = OK if running else FAIL
        status = "running" if running else "not running"
        print(f"  {mark} {svc:<14} {status}")
        if not running:
            all_ok = False

    # API endpoint check
    ok, detail = _check_api_health()
    mark = OK if ok else FAIL
    print(f"  {mark} {'api /health':<14} {detail}")
    if not ok:
        all_ok = False

    print()
    if all_ok:
        print("All services healthy.")
    else:
        print("Some services are unhealthy.")
