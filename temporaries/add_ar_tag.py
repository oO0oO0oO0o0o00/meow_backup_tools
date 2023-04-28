from pathlib import Path

import boto3

from consts import Consts

if __name__ == '__main__':
    s3 = boto3.client("s3")
    for obj in s3.list_objects_v2(
            Bucket=Consts.bak_bucket, Prefix="phonebak"
    )['Contents']:
        if obj['StorageClass'] != 'STANDARD':
            continue
        key = obj['Key']
        tags = s3.get_object_tagging(
            Bucket=Consts.bak_bucket, Key=key
        )["TagSet"]
        tag_keys = set(tag["Key"] for tag in tags)
        if "archive" in tag_keys or "MD5" not in tag_keys:
            continue
        tags.append({
            'Key': "archive", 'Value': "yes"
        })
        s3.put_object_tagging(
            Bucket=Consts.bak_bucket,
            Key=key,
            Tagging={'TagSet': tags},
        )
