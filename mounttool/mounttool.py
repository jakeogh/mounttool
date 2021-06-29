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
from pathlib import Path
from typing import ByteString
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence

import click
import sh
from enumerate_input import enumerate_input
from psutil import disk_partitions


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


def validate_slice(slice_syntax):
    assert isinstance(slice_syntax, str)
    for c in slice_syntax:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '[', ']', ':']:
            raise ValueError(slice_syntax)
    return slice_syntax


def block_special_path_is_mounted(path,
                                  verbose: bool,
                                  debug: bool,
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
                    verbose: bool,
                    debug: bool,
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


def mount_something(path: Path,
                    mount_type: str,
                    source: Path,
                    verbose: bool,
                    debug: bool,
                    ):

    assert mount_type in ['proc', 'rbind']
    if mount_type == 'rbind':
        assert source
        assert source.is_absolute()
    assert isinstance(path, Path)
    if source:
        assert isinstance(source, Path)

    if path_is_mounted(path, verbose=verbose, debug=debug,):
        return

    if mount_type == 'proc':
        mount_command = sh.mount.bake('-t', 'proc', 'none', path)
    elif mount_type == 'rbind':
        mount_command = sh.mount.bake('--rbind', source.as_posix(), path)
    else:
        raise ValueError('unknown mount type: {}'.format(mount_type))

    mount_command()


@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def mounttool(ctx,
              verbose: bool,
              debug: bool,
              ):

    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug


@click.command()
@click.argument("paths", type=str, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def info(ctx,
         paths,
         verbose: bool,
         debug: bool,
         ):

    null = not False
    end = '\n'
    if null:
        end = '\x00'
    if sys.stdout.isatty():
        end = '\n'

    ctx.ensure_object(dict)
    if verbose:
        ctx.obj['verbose'] = verbose
    verbose = ctx.obj['verbose']
    if debug:
        ctx.obj['debug'] = debug
    debug = ctx.obj['debug']

    ctx.obj['end'] = end
    ctx.obj['null'] = null

    iterator = paths

    for index, path in enumerate_input(iterator=iterator,
                                       null=null,
                                       progress=False,
                                       skip=None,
                                       head=None,
                                       tail=None,
                                       debug=debug,
                                       verbose=verbose,):
        path = Path(path).expanduser()

        if verbose:
            ic(index, path)

        ic(path_is_mounted(path=path, verbose=verbose, debug=debug))
        ic(block_special_path_is_mounted(path=path, verbose=verbose, debug=debug))
