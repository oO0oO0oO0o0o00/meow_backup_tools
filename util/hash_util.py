import hashlib
from pathlib import Path


def get_md5_of_file(file: Path):
    file_hash = hashlib.md5()
    with open(file, "rb") as fp:
        while chunk := fp.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()