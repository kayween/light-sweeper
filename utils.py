import os
import datetime

from pathlib import Path


def get_time_stamp():
    dt_str = str(datetime.datetime.now())
    ret = dt_str.split()[0] + '-' + dt_str.split()[1].split('.')[0]
    return ret


def create_latest_symlink(target: str):
    """
    Args:
        target: The target foler to link.
    """
    parent = os.path.join(target, os.pardir)

    symlink = Path(os.path.join(parent, "latest"))

    if symlink.exists():
        assert symlink.is_symlink()
        symlink.unlink()

    symlink.symlink_to(os.path.join(parent, target))
