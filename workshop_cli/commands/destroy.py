"""Destroy Docker Compose services, volumes, and images."""

import subprocess

from workshop_cli.utils.spinner import run_with_spinner


def cmd_destroy(args):
    cmd = [
        "docker",
        "compose",
        "down",
        "--volumes",
        "--remove-orphans",
        "--rmi",
        args.rmi,
    ]
    run_with_spinner(
        "Stopping and removing containers, networks, volumes, and images...",
        subprocess.run,
        cmd,
        capture_output=True,
    )

    if args.prune_build_cache:
        run_with_spinner(
            "Pruning Docker build cache...",
            subprocess.run,
            ["docker", "builder", "prune", "--force"],
            capture_output=True,
        )
