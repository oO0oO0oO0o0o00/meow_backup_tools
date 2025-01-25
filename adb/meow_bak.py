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
import os
from pathlib import PurePosixPath
import subprocess
import datetime
import posixpath
from typing import List
from loguru import logger

from .adb_file_system import AdbFileSystem
from .file_syncer import FileSyncer
from .sync_config import SyncConfig
from .adb_file_system import AdbFileSystem
from .file_syncer import FixPath
from .sync_config import SyncConfig
from .time_range_parser import parse_date


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


def do(date_digits: str, keep_days: int, dirs: List[str], bak_home: str, *, excludes: List[str]):
    adb = AdbFileSystem([b'adb'])
    to_date = parse_date(date_digits)
    to_date -= datetime.timedelta(days=keep_days)
    bak_long_home = posixpath.join(bak_home, date_digits, "storage")
    bak_recent_home = posixpath.join(bak_home, date_digits, "storage-keep")
    os.makedirs(bak_long_home, exist_ok=True)
    os.makedirs(bak_recent_home, exist_ok=True)
    to_time = int(to_date.timestamp())
    for bak_home, time_range, del_source in [
        (bak_long_home, [0, to_time], True),
        (bak_recent_home, [to_time, None], False),
    ]:
        cfg = SyncConfig(
            excludes=excludes, remote_to_local=True, delete_missing=False, del_source=del_source,
            allow_overwrite=True, allow_replace=True, time_range=time_range)
        for bak_src in dirs:
            bak_src = str(PurePosixPath("/sdcard") / bak_src)
            bak_src, bak_dst = FixPath(
                os.fsencode(bak_src), os.fsencode(bak_home))
            do_sync(adb, bak_dst, bak_src, cfg)
