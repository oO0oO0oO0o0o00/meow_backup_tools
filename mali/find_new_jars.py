""" 找未提取的jar """
import itertools
from pathlib import Path

from loguru import logger

from util.hash_util import get_md5_of_file


def main():
    src = Path(r"F:\LOFL\before-2015\2013-MSD塞班剩余1231")
    lib = Path(r"F:\LOFL\2013-swf")
    # patterns = ["*.sis", "*.sisx"]
    patterns = ["*.swf"]
    # patterns = ["*.jar"]
    lookup = set()
    for file in get_matches(lib, patterns):
        lookup.add(get_md5_of_file(file))
    for file in get_matches(src, patterns):
        rel: Path = file.relative_to(src)
        if rel.is_relative_to("private"):
            continue
        if get_md5_of_file(file) in lookup:
            file.unlink()
        else:
        # if get_md5_of_file(file) not in lookup:
            logger.warning(str(rel))


def get_matches(path, patterns):
    return itertools.chain(*[path.rglob(pattern) for pattern in patterns])


if __name__ == '__main__':
    main()
