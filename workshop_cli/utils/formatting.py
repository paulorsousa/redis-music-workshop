"""Output formatting helpers."""

# ANSI color helpers
_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"

OK = f"{_GREEN}✓{_RESET}"
FAIL = f"{_RED}✗{_RESET}"


def format_bytes(b):
    """Return a human-readable byte size string."""
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KiB"
    return f"{b / (1024 * 1024):.1f} MiB"
