"""Shared helpers for service modules."""


def decode_redis(value) -> str:
    """Decode a Redis response value to str."""
    return value if isinstance(value, str) else value.decode()
