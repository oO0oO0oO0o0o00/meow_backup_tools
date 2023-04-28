"""Check whether locally-stored hashes matches those stored in S3."""
from pathlib import Path

import boto3

from archives import hash_archives

if __name__ == '__main__':
    s3 = boto3.client("s3")
    root = Path(r"G:\LOAR")
    hash_archives.process_tree(
        root,
        lambda path: hash_archives.check_online(
            path, root, s3, "rbq2012-kittenal-backups", {})
    )
