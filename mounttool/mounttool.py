#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=fixme                           # [W0511] todo is encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement
from __future__ import annotations

import os
from pathlib import Path

import click
import sh
from asserttool import ic
from asserttool import icp
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from globalverbose import gvd
from psutil import disk_partitions
from unmp import unmp


def block_special_path_is_mounted(
    path,
    verbose: bool | int | float = False,
):
    assert path
    path = Path(path).expanduser()
    assert isinstance(path, Path)
    for mount in disk_partitions():
        # print(mount)
        if path.as_posix() in mount.device:
            return True
    return False


def path_is_mounted(
    path,
    verbose: bool | int | float = False,
):  # todo test with angryfiles
    assert path
    path = Path(path).expanduser()
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
    verbose: bool | int | float = False,
):
    ic(
        mountpoint,
        mount_type,
        source,
    )

    assert mount_type in ["proc", "bind", "rbind", "tmpfs"]
    if mount_type in ["bind", "rbind"]:
        assert source
        assert source.is_absolute()

    assert isinstance(mountpoint, Path)
    if source:
        assert isinstance(source, Path)

    # lazy mistake
    # if mountpoint_is_mounted(mountpoint,):
    #    return

    slave_command = None
    if mount_type == "proc":
        mount_command = sh.mount.bake("-t", "proc", "none", mountpoint)
    elif mount_type == "tmpfs":
        mount_command = sh.mount.bake("-t", "tmpfs", "none", mountpoint)
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

    mount_command()
    if slave_command:
        slave_command()


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def mounttool(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
):
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()
    else:
        ic.enable()

    if verbose_inf:
        gvd.enable()


@click.command()
@click.argument("paths", type=str, nargs=-1)
@click_add_options(click_global_options)
@click.pass_context
def info(
    ctx,
    paths,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
):
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()
    else:
        ic.enable()

    if verbose_inf:
        gvd.enable()

    if paths:
        iterator = paths
    else:
        iterator = unmp(
            valid_types=[
                bytes,
            ],
        )

    for index, path in enumerate(iterator):
        path = Path(path).expanduser()
        ic(index, path)
        icp(
            path_is_mounted(
                path=path,
            )
        )
        icp(
            block_special_path_is_mounted(
                path=path,
            )
        )
