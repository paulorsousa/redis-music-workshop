"""Shared utilities for the workshop CLI."""

from workshop_cli.utils.api import API_URL, api_call
from workshop_cli.utils.formatting import FAIL, OK, format_bytes
from workshop_cli.utils.identity import NAMESPACE, derive_user_id
from workshop_cli.utils.progress import ProgressTracker
from workshop_cli.utils.spinner import spinner

__all__ = [
    "API_URL",
    "FAIL",
    "NAMESPACE",
    "OK",
    "ProgressTracker",
    "api_call",
    "derive_user_id",
    "format_bytes",
    "spinner",
]
