"""Generate or check hash for local archives, or compare with hash in S3."""

import enum
from collections import defaultdict
from pathlib import Path
from typing import Mapping

from loguru import logger

from util.hash_util import get_md5_of_file

included_extensions = {"zip", "7z", "tgz", "gz", "bz", "lzma", "tar"}


def process_tree(path: Path, fn):
    log_fns = {
        _ResultLevel.info: logger.info,
        _ResultLevel.warn: logger.warning,
        _ResultLevel.error: logger.error,
        _ResultLevel.fatal: logger.error
    }
    results = defaultdict(list)
    for file in path.rglob("*"):
        if file.suffix[1:].lower() in included_extensions:
            result = fn(file)
            disp_path = file.relative_to(path)
            log_fns[result.level]("{}: {}", disp_path, result.name)
            if result.level > _ResultLevel.info:
                results[result.level].append((disp_path, result.name))
    logger.info("All done.")
    newline = "\n"
    for level in [_ResultLevel.warn, _ResultLevel.error, _ResultLevel.fatal]:
        if (files := results.get(level)) is not None:
            log_fns[level](
                f"These files failed with {level.name}:\n {newline.join([f'{file}: {reason}' for file, reason in files])}")


def check_online(path: Path, local_root: Path, s3, bucket: str, mappings: Mapping[str, str]):
    verified_path = path.parent / f"{path.name}.s3-ok.txt"
    if verified_path.exists():
        return Results.Skipped
    local_md5 = _read_locally_saved_hash(path)
    if local_md5 is None:
        return Results.LocalHashMissing
    key = str(path.relative_to(local_root).as_posix())
    for src, dst in mappings.items():
        if key.startswith(src):
            key = dst + key[len(src):]
    try:
        response = s3.get_object_tagging(
            Bucket=bucket,
            Key=key
        )
    except Exception as e:
        if type(e).__name__ == "NoSuchKey":
            return Results.RemoteFileMissing
        raise e
    remote_hash = None
    for tag in response["TagSet"]:
        if tag["Key"] == "MD5":
            remote_hash = tag["Value"]
    if remote_hash is None:
        return Results.RemoteHashMissing
    if local_md5 != remote_hash:
        return Results.DoesNotMatch
    verified_path.touch(exist_ok=True)
    return Results.OK


def generate_hash(path: Path):
    hash_path = _get_hash_path(path)
    if hash_path.exists():
        return Results.Skipped
    md5 = get_md5_of_file(path)
    with open(hash_path, 'w') as fp:
        fp.write(md5)
    return Results.OK


def _read_locally_saved_hash(path):
    hash_path = _get_hash_path(path)
    if not hash_path.exists():
        # logger.warning("Cannot check {}: hash exists not.", path)
        return None
    with open(hash_path, 'r') as fp:
        return fp.read().strip()


def _get_hash_path(path):
    return path.parent / f"{path.name}.md5"


class _ResultLevel(enum.IntEnum):
    info = 200
    warn = 300
    error = 400
    fatal = 500


class Result:

    def __init__(self, name: str, level: _ResultLevel):
        self.name = name
        self.level = level


class Results:
    OK = Result("ok", _ResultLevel.info)
    Skipped = Result("skipped", _ResultLevel.info)
    LocalHashMissing = Result("local hash missing", _ResultLevel.warn)
    RemoteFileMissing = Result("remote file missing", _ResultLevel.warn)
    RemoteHashMissing = Result("remote hash missing", _ResultLevel.warn)
    DoesNotMatch = Result("does not match", _ResultLevel.error)

# if __name__ == '__main__':
#     main()
# process_tree(Path(r"G:\LOAR"), Mode.generate)
