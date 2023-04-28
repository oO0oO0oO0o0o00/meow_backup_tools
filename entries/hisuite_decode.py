from pathlib import Path

from loguru import logger

from util import datetime_util
from hisuite.kobackupdec import main

pathwood = "aA" + "1" * 6
bak_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2022-10-12 09.20.01"
bak_dst_root = Path("D:\phonebak\tmp")


def _bak():
    dst = bak_dst_root / datetime_util.to66()
    main(pathwood, bak_src, str(dst), expandtar=False, writable=True)


def do():
    twin_suffix = "#Twin.tar"
    logger.info("Backing up...")
    _bak()
    twins = []
    for file in Path(bak_src).iterdir():
        if file.name.endswith(twin_suffix):
            name = file.name
            master = file.parent / f"{name[:len(name) - len(twin_suffix)]}.tar"
            if not master.exists():
                logger.warning(f"Master file for {name} does not exists.")
            else:
                twins.append((master, file))
    if len(twins) <= 0:
        return
    logger.info("Done.")
    input("Process twin apps? Ctrl-C if not.")
    for master, twin in twins:
        master.rename(master.parent / f"{master.stem}.master{master.suffix}")
        twin.rename(master)
    logger.info("Backing up twin...")
    _bak()
    logger.info("All done. Wish you a good memory and disk.")


if __name__ == '__main__':
    do()
