#!/usr/bin/env python3

# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Sync files from/to an Android device."""

from __future__ import unicode_literals
import argparse
import os
import subprocess

from loguru import logger

from . import time_range_parser
from .adb_file_system import AdbFileSystem
from .file_syncer import FileSyncer, ExpandWildcards, FixPath
from .sync_config import SyncConfig


def list2cmdline_patch(seq):
    """
    # windows compatible
    Translate a sequence of arguments into a command line
    string, using the same rules as the MS C runtime:

    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # or search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        #
        if type(arg) == bytes:
            try:
                arg = arg.decode()
            except(UnicodeDecodeError):
                print('debug:')
                print(arg)
                arg = arg.replace(b'\xa0', b'\xc2\xa0')
                arg = arg.decode()
            pass

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf) * 2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


if os.name == 'nt':
    subprocess.list2cmdline = list2cmdline_patch


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Synchronize a directory between an Android device and the '
                    'local file system')
    parser.add_argument(
        'source',
        metavar='SRC',
        type=str,
        nargs='+',
        help='The directory to read files/directories from. '
             'This must be a local path if -R is not specified, '
             'and an Android path if -R is specified. If SRC does '
             'not end with a final slash, its last path component '
             'is appended to DST (like rsync does).')
    parser.add_argument(
        'destination',
        metavar='DST',
        type=str,
        help='The directory to write files/directories to. '
             'This must be an Android path if -R is not specified, '
             'and a local path if -R is specified.')
    parser.add_argument(
        '--adb',
        metavar='COMMAND',
        default='adb',
        type=str,
        help='Use the given adb binary and arguments.')
    parser.add_argument(
        '--device',
        action='store_true',
        help='Directs command to the only connected USB device; '
             'returns an error if more than one USB device is present. '
             'Corresponds to the "-d" option of adb.')
    parser.add_argument(
        '--emulator',
        action='store_true',
        help='Directs command to the only running emulator; '
             'returns an error if more than one emulator is running. '
             'Corresponds to the "-e" option of adb.')
    parser.add_argument(
        '-s',
        '--serial',
        metavar='DEVICE',
        type=str,
        help='Directs command to the device or emulator with '
             'the given serial number or qualifier. Overrides '
             'ANDROID_SERIAL environment variable. Use "adb devices" '
             'to list all connected devices with their respective serial number. '
             'Corresponds to the "-s" option of adb.')
    parser.add_argument(
        '-H',
        '--host',
        metavar='HOST',
        type=str,
        help='Name of adb server host (default: localhost). '
             'Corresponds to the "-H" option of adb.')
    parser.add_argument(
        '-P',
        '--port',
        metavar='PORT',
        type=str,
        help='Port of adb server (default: 5037). '
             'Corresponds to the "-P" option of adb.')
    parser.add_argument(
        '-R',
        '--reverse',
        action='store_true',
        help='Reverse sync (pull, not push).')
    parser.add_argument(
        '-x',
        '--exclude',
        metavar='EXCLUDE',
        type=str,
        help='Glob exclude pattern (multiple with comma separation)')
    parser.add_argument(
        '-2',
        '--two-way',
        action='store_true',
        help='Two-way sync (compare modification time; after '
             'the sync, both sides will have all files in the '
             'respective newest version. This relies on the clocks '
             'of your system and the device to match.')
    parser.add_argument(
        '-d',
        '--delete',
        action='store_true',
        help='Delete files from DST that are not present on '
             'SRC. Mutually exclusive with -2.')
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Allow deleting files/directories when having to '
             'replace a file by a directory or vice versa. This is '
             'disabled by default to prevent large scale accidents.')
    parser.add_argument(
        '-n',
        '--no-clobber',
        action='store_true',
        help='Do not ever overwrite any '
             'existing files. Mutually exclusive with -f.')
    parser.add_argument(
        '-L',
        '--copy-links',
        action='store_true',
        help='transform symlink into referent file/dir')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Do not do anything - just show what would be done.')
    parser.add_argument(
        '-t',
        '--time-range',
        metavar='890604-191001.120000',
        type=str,
        help='Date and time range begin-end, begin- or 0-end, format of begin and end is yymmdd[.hhmmss]')
    parser.add_argument(
        '--del-source',
        action='store_true',
        help='Delete source after syncing')
    args = parser.parse_args()

    localpatterns = [os.fsencode(x) for x in args.source]
    remotepath = os.fsencode(args.destination)
    adb_args = os.fsencode(args.adb).split(b' ')
    if args.device:
        adb_args += [b'-d']
    if args.emulator:
        adb_args += [b'-e']
    if args.serial:
        adb_args += [b'-s', os.fsencode(args.serial)]
    if args.host:
        adb_args += [b'-H', os.fsencode(args.host)]
    if args.port:
        adb_args += [b'-P', os.fsencode(args.port)]
    adb = AdbFileSystem(adb_args)

    # Expand wildcards, but only on the remote side.
    localpaths = []
    remotepaths = []
    if args.reverse:
        for pattern in localpatterns:
            for src in ExpandWildcards(adb, pattern):
                src, dst = FixPath(src, remotepath)
                localpaths.append(src)
                remotepaths.append(dst)
    else:
        for src in localpatterns:
            src, dst = FixPath(src, remotepath)
            localpaths.append(src)
            remotepaths.append(dst)

    cfg = SyncConfig()
    cfg.delete_missing = args.delete
    cfg.allow_replace = args.force
    cfg.allow_overwrite = not args.no_clobber
    cfg.copy_links = args.copy_links
    cfg.dry_run = args.dry_run
    cfg.del_source = args.del_source

    if args.time_range:
        try:
            cfg.time_range = time_range_parser.parse_time_range(args.time_range)
        except:
            logger.error("time range format error: {}", args.time_range)
            parser.print_help()
            return

    try:
        cfg.excludes = args.exclude.split(",")
    except:
        cfg.excludes = args.exclude if args.exclude else ""
    cfg.local_to_remote = True
    cfg.remote_to_local = False
    if args.two_way:
        cfg.local_to_remote = True
        cfg.remote_to_local = True
    if args.reverse:
        cfg.local_to_remote, cfg.remote_to_local = cfg.remote_to_local, cfg.local_to_remote
        localpaths, remotepaths = remotepaths, localpaths
    if cfg.allow_replace and not cfg.allow_overwrite:
        logger.error('--no-clobber and --force are mutually exclusive.')
        parser.print_help()
        return
    if cfg.delete_missing and cfg.local_to_remote and cfg.remote_to_local:
        logger.error('--delete and --two-way are mutually exclusive.')
        parser.print_help()
        return
    if cfg.del_source and (
            (cfg.delete_missing or cfg.local_to_remote and cfg.remote_to_local) or not cfg.allow_overwrite
    ):
        logger.error("deleting source means moving, which is incompatible with deleting missing or 2-way")
        parser.print_help()
        return
    if cfg.del_source:
        cfg.allow_replace = True

    # Two-way sync is only allowed with disjoint remote and local path sets.
    if (cfg.remote_to_local and cfg.local_to_remote) or cfg.delete_missing:
        if ((cfg.remote_to_local and len(localpaths) != len(set(localpaths))) or
                (cfg.local_to_remote and len(remotepaths) != len(set(remotepaths)))):
            logger.error(
                '--two-way and --delete are only supported for disjoint sets of '
                'source and destination paths (in other words, all SRC must '
                'differ in basename).')
            parser.print_help()
            return

    for i in range(len(localpaths)):
        logger.info('Sync: local {}, remote {}',
                    localpaths[i].decode("utf-8", "replace"),
                    remotepaths[i].decode("utf-8", "replace"))
        do_sync(adb, localpaths[i], remotepaths[i], cfg)


def do_sync(adb: AdbFileSystem, localpath: bytes, remotepath: bytes, cfg: SyncConfig):
    syncer = FileSyncer(adb, localpath, remotepath, cfg)
    if not syncer.IsWorking():
        logger.error('Device not connected or not working.')
        return
    syncer.ScanAndDiff()
    syncer.PerformDeletions()
    syncer.PerformOverwrites()
    syncer.PerformCopies()
    syncer.TimeReport()


if __name__ == '__main__':
    main()
