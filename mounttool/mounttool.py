#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement

# TODO: https://docs.python.org/3.7/library/pathlib.html#pathlib.Path.is_mount

import os
import sys
from math import inf
from pathlib import Path
from typing import ByteString
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import click
import sh
from asserttool import ic
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from eprint import eprint
from psutil import disk_partitions
from unmp import unmp


def block_special_path_is_mounted(path,
                                  verbose: Union[bool, int, float],
                                  ):
    assert path
    path = Path(path).expanduser()
    assert isinstance(path, Path)
    for mount in disk_partitions():
        #print(mount)
        if path.as_posix() in mount.device:
            return True
    return False


def path_is_mounted(path,
                    verbose: Union[bool, int, float],
                    ):  # todo test with angryfiles
    assert path
    path = Path(path).expanduser()
    assert isinstance(path, Path)
    for mount in disk_partitions():
        if verbose:
            ic(mount)
        if mount.mountpoint == path.as_posix():
            return True
    if os.path.ismount(path):
        return True
    return False


def mount_something(*,
                    mountpoint: Path,
                    mount_type: str,
                    source: Optional[Path],
                    verbose: Union[bool, int, float],
                    ):
    if verbose:
        ic(mountpoint, mount_type, source,)

    assert mount_type in ['proc', 'rbind', 'tmpfs']
    if mount_type == 'rbind':
        assert source
        assert source.is_absolute()

    assert isinstance(mountpoint, Path)
    if source:
        assert isinstance(source, Path)

    # lazy mistake
    #if mountpoint_is_mounted(mountpoint, verbose=verbose, ):
    #    return

    if mount_type == 'proc':
        mount_command = sh.mount.bake('-t', 'proc', 'none', mountpoint)
    elif mount_type == 'tmpfs':
        mount_command = sh.mount.bake('-t', 'tmpfs', 'none', mountpoint)
    elif mount_type == 'rbind':
        mount_command = sh.mount.bake('--rbind', source.as_posix(), mountpoint)
    else:
        raise ValueError('unknown mount type: {}'.format(mount_type))

    mount_command()


@click.group(no_args_is_help=True)
@click_add_options(click_global_options)
@click.pass_context
def mounttool(ctx,
              verbose: Union[bool, int, float],
              verbose_inf: bool,
              ):

    tty, verbose = tv(ctx=ctx,
                      verbose=verbose,
                      verbose_inf=verbose_inf,
                      )


@click.command()
@click.argument("paths", type=str, nargs=-1)
@click_add_options(click_global_options)
@click.pass_context
def info(ctx,
         paths,
         verbose: Union[bool, int, float],
         verbose_inf: bool,
         ):

    tty, verbose = tv(ctx=ctx,
                      verbose=verbose,
                      verbose_inf=verbose_inf,
                      )

    if paths:
        iterator = paths
    else:
        iterator = unmp(valid_types=[bytes,], verbose=verbose,)

    for index, path in enumerate(iterator):
        path = Path(path).expanduser()
        if verbose:
            ic(index, path)
        ic(path_is_mounted(path=path, verbose=verbose,))
        ic(block_special_path_is_mounted(path=path, verbose=verbose,))
