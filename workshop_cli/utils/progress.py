"""Thread-safe progress bar for bulk operations."""

import threading

from workshop_cli.utils.formatting import FAIL


class ProgressTracker:
    """Thread-safe progress tracker that overwrites a single terminal line."""

    def __init__(self, total, label="Progress"):
        self.total = total
        self.label = label
        self._done = 0
        self._errors = 0
        self._lock = threading.Lock()
        self._print()

    def _bar(self):
        pct = self._done / self.total if self.total else 1
        width = 25
        filled = int(width * pct)
        return f"[{'█' * filled}{'·' * (width - filled)}]"

    def _print(self):
        err_str = f"  {FAIL} {self._errors} errors" if self._errors else ""
        print(
            f"\r  {self.label} {self._bar()} {self._done}/{self.total}{err_str}",
            end="",
            flush=True,
        )

    def advance(self, error=False):
        with self._lock:
            self._done += 1
            if error:
                self._errors += 1
            self._print()

    def finish(self):
        print()  # newline after the progress line

    @property
    def errors(self):
        return self._errors

    @property
    def done(self):
        return self._done
