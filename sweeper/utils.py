import os
from datetime import datetime

from pathlib import Path


def get_time_stamp():
    return datetime.now().strftime("%Y-%m-%d-%H.%M.%S")


def create_latest_symlink(target: str):
    """
    Args:
        target: The target foler to link.
    """
    parent = os.path.dirname(target)
    base = os.path.basename(target)

    symlink = Path(os.path.join(parent, "latest"))

    if symlink.exists():
        assert symlink.is_symlink()
        symlink.unlink()

    symlink.symlink_to(os.path.join(base))
