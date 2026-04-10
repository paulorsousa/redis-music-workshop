"""Animated terminal spinner."""

import threading

from workshop_cli.utils.formatting import OK


def spinner(message, stop_event):
    """Animate a spinner on a single line until *stop_event* is set."""
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    while not stop_event.is_set():
        print(f"\r  {frames[i % len(frames)]} {message}", end="", flush=True)
        i += 1
        stop_event.wait(0.1)
    print(f"\r  {OK} {message} done")


def run_with_spinner(message, fn, *args, **kwargs):
    """Run *fn* while showing a spinner with *message*. Returns fn's result."""
    stop = threading.Event()
    t = threading.Thread(target=spinner, args=(message, stop))
    t.start()
    try:
        result = fn(*args, **kwargs)
    finally:
        stop.set()
        t.join()
    return result
