#!/usr/bin/env python3
# -*- coding: utf8 -*-

from __future__ import annotations

import os
from pathlib import Path

import sh
from asserttool import ic
from pathtool import path_is_block_special
from psutil import disk_partitions

# from unmp import unmp


def block_special_path_is_mounted(
    path,
):
    assert path
    path = Path(path).expanduser()
    path = path.resolve()
    assert path_is_block_special(path, symlink_ok=False)
    assert isinstance(path, Path)
    for mount in disk_partitions():
        # print(mount)
        if path.as_posix() in mount.device:
            return True
    return False


def path_is_mounted(
    path,
):  # todo test with angryfiles
    assert path
    path = Path(path).expanduser()
    path = path.resolve()
    assert isinstance(path, Path)
    for mount in disk_partitions():
        ic(mount)
        if mount.mountpoint == path.as_posix():
            return True
    if os.path.ismount(path):
        return True
    return False


def mount_something(
    *,
    mountpoint: Path,
    mount_type: str,
    slave: bool,
    source: None | Path,
):
    ic(
        mountpoint,
        mount_type,
        source,
    )

    assert mount_type in {"proc", "bind", "rbind", "tmpfs"}
    if mount_type in {"bind", "rbind"}:
        assert source
        assert source.is_absolute()

    assert isinstance(mountpoint, Path)
    if source:
        assert isinstance(source, Path)

    # lazy mistake
    # if mountpoint_is_mounted(mountpoint,):
    #    return

    slave_command = None
    mount_command = None
    if mount_type == "proc":
        mount_command = sh.mount.bake(
            "-t",
            "proc",
            "none",
            mountpoint,
        )
    elif mount_type == "tmpfs":
        mount_command = sh.mount.bake(
            "-t",
            "tmpfs",
            "none",
            mountpoint,
        )
    elif mount_type == "bind":
        if source:
            mount_command = sh.mount.bake("--bind", source.as_posix(), mountpoint)
            if slave:
                slave_command = sh.mount.bake("--make-slave", mountpoint)
    elif mount_type == "rbind":
        if source:
            mount_command = sh.mount.bake("--rbind", source.as_posix(), mountpoint)
            if slave:
                slave_command = sh.mount.bake("--make-rslave", mountpoint)
    else:
        raise ValueError(f"unknown mount type: {mount_type}")

    assert mount_command
    if mount_command:
        mount_command()
    if slave_command:
        slave_command()


# @click.group(no_args_is_help=True, cls=AHGroup)
# @click_add_options(click_global_options)
# @click.pass_context
# def mounttool(
#    ctx,
#    verbose_inf: bool,
#    dict_output: bool,
#    verbose: bool = False,
# ):
#    tty, verbose = tvicgvd(
#        ctx=ctx,
#        verbose=verbose,
#        verbose_inf=verbose_inf,
#        ic=ic,
#        gvd=gvd,
#    )
#
#
# @click.command()
# @click.argument("paths", type=str, nargs=-1)
# @click_add_options(click_global_options)
# @click.pass_context
# def info(
#    ctx,
#    paths,
#    verbose_inf: bool,
#    dict_output: bool,
#    verbose: bool = False,
# ):
#    tty, verbose = tvicgvd(
#        ctx=ctx,
#        verbose=verbose,
#        verbose_inf=verbose_inf,
#        ic=ic,
#        gvd=gvd,
#    )
#
#    if paths:
#        iterator = paths
#    else:
#        iterator = unmp(
#            valid_types=[
#                bytes,
#            ],
#        )
#
#    for index, path in enumerate(iterator):
#        path = Path(path).expanduser()
#        ic(index, path)
#        icp(
#            path_is_mounted(
#                path=path,
#            )
#        )
#        icp(
#            block_special_path_is_mounted(
#                path=path,
#            )
#        )
