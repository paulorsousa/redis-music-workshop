"""Compute and load song embeddings."""

from workshop_cli.utils import api_call
from workshop_cli.utils.spinner import run_with_spinner


def cmd_load_embeddings(args):
    try:
        data, elapsed = run_with_spinner(
            "Loading embeddings (this may take a while)...",
            api_call,
            "/admin/load-embeddings",
            method="POST",
        )
        print(
            f"  ✓ {data['loaded']} song embeddings loaded ({data['dimensions']} dimensions)"
        )
        print(f"  ⏱ {elapsed:.2f} s")
    except Exception as e:
        print(f"  ✗ Error: {e}")
