"""User identity helpers."""

import uuid

NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def derive_user_id(username: str) -> str:
    """Derive a deterministic UUID-v5 user ID from a username."""
    return str(uuid.uuid5(NAMESPACE, username))
