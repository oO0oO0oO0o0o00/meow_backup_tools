import os
for key in ["PROXY", "HTTP_PROXY", "HTTPS_PROXY"]:
    os.environ.pop(key, None)

import boto3
from loguru import logger


def demo_upload():
    s3 = boto3.client('s3')
    bucket = "rbq2012-kittenal-backups"
    key = "phonebak/test-mul.bin"
    part_size = 5 * 1024 * 1024
    path = r"D:\test.bin"

    id = s3.create_multipart_upload(
        Bucket=bucket,
        Key=key
    )['UploadId']
    logger.info("Began uploading with id {}.", id)
    part_number = 1
    parts = []

    with open(path, "rb") as fp:
        while part := fp.read(part_size):
            resp = s3.upload_part(
                Body=part,
                Bucket=bucket,
                Key=key,
                PartNumber=part_number,
                UploadId=id
            )
            parts.append({'ETag': resp['ETag'], 'PartNumber': part_number})
            logger.info("Uploaded part {} for id {}: {}.", part_number, id, resp)
            part_number += 1

    resp = s3.complete_multipart_upload(
        Bucket=bucket,
        Key=key,
        MultipartUpload={
            'Parts': parts
        },
        UploadId=id,
    )
    logger.info("Completed upload id {}: {}", id, resp)


if __name__ == '__main__':
    demo_upload()
