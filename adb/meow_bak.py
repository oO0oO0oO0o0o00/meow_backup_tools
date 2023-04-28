import datetime
import os
import posixpath
from pathlib import Path, PosixPath
from typing import List
from . import adb_sync
from .adb_file_system import AdbFileSystem
from .file_syncer import FixPath
from .sync_config import SyncConfig
from .time_range_parser import parse_date


def __main__():
    do("221010", [
        # "/sdcard/DCIM",
        # "/sdcard/documents",
        # "/sdcard/Download",
        # "/sdcard/Pictures",
        # "/sdcard/Sounds",
        # "/sdcard/tieba",
        # "/sdcard/Tencent/QQ_Images",
        "/sdcard/Tencent/QQ_Videos",
        # "/sdcard/Movies",
        # "/sdcard/Tencent/MicroMsg/WeiXin",
        # "/sdcard/Android/data/com.tencent.mm/MicroMsg/Download",
        # "/sdcard/Android/data/com.tencent.mobileqq/Tencent/QQfile_recv",

    ], "D:/phonebak/meow_bak_sd", excludes=[".*"])


def do(date_digits: str, dirs: List[str], bak_home: str, *, excludes: List[str]):
    adb = AdbFileSystem([b'adb'])
    to_date = parse_date(date_digits)
    to_date -= datetime.timedelta(days=90)
    bak_home = posixpath.join(bak_home, date_digits, "storage")
    os.makedirs(bak_home, exist_ok=True)
    bak_home = os.fsencode(bak_home)
    cfg = SyncConfig(
        excludes=excludes, remote_to_local=True, delete_missing=False, del_source=True,
        allow_overwrite=True, allow_replace=True, time_range=[0, int(to_date.timestamp())]
    )
    for bak_src in dirs:
        bak_src, bak_dst = FixPath(os.fsencode(bak_src), bak_home)
        # print(bak_home, os.fsencode(bak_src), cfg)
        # SyncConfig(excludes='.*', local_to_remote=False, remote_to_local=True, delete_missing=False, allow_overwrite=True, allow_replace=True, copy_links=False, dry_run=False, time_range=[0, 1623513600], del_source=False)
        # SyncConfig(excludes='.*', local_to_remote=False, remote_to_local=True, delete_missing=False, allow_overwrite=True, allow_replace=False, copy_links=False, dry_run=False, time_range=None, del_source=False)
        adb_sync.do_sync(adb, bak_dst, bak_src, cfg)


if __name__ == '__main__':
    __main__()
