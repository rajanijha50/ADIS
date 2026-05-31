import hashlib
from datetime import datetime, timedelta

# helper functions for
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def now(offset_minutes: int = 0) -> str:
    """Return current local time as a formatted string."""
    return (datetime.now() + timedelta(minutes=offset_minutes)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
