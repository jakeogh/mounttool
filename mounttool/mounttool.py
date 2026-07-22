#!/usr/bin/env python3

from pathlib import Path

import hs
from asserttool import ic
from pathtool import path_is_block_special
from psutil import disk_partitions

_mount = hs.Command("mount")


def block_special_path_is_mounted(path: Path) -> bool:
    assert path
    path = Path(path).expanduser().resolve()
    assert path_is_block_special(path, symlink_ok=False)
    for mount in disk_partitions():
        if path.as_posix() in mount.device:
            return True
    return False


def path_is_mounted(path: Path) -> bool:
    assert path
    path = Path(path).expanduser().resolve()
    for mount in disk_partitions():
        ic(mount)
        if mount.mountpoint == path.as_posix():
            return True
    return path.is_mount()


def mount_something(
    *,
    mountpoint: Path,
    mount_type: str,
    slave: bool,
    source: None | Path,
) -> None:
    ic(mountpoint, mount_type, source)

    match mount_type:
        case "proc" | "tmpfs":
            _mount("-t", mount_type, "none", mountpoint.as_posix())
        case "bind":
            assert source
            assert source.is_absolute()
            _mount("--bind", source.as_posix(), mountpoint.as_posix())
            if slave:
                _mount("--make-slave", mountpoint.as_posix())
        case "rbind":
            assert source
            assert source.is_absolute()
            _mount("--rbind", source.as_posix(), mountpoint.as_posix())
            if slave:
                _mount("--make-rslave", mountpoint.as_posix())
        case _:
            raise ValueError(f"unknown mount type: {mount_type}")
