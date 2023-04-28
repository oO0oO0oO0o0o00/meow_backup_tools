import hashlib
import urllib.parse
import boto3


def lambda_handler(event, context):
    print(event)
    s3_info = event['Records'][0]['s3']
    bucket = s3_info['bucket']['name']
    if s3_info['object']['size'] <= 0:
        print("0 size, maybe a folder, skipping.")
        return return_val(200)
    key = urllib.parse.unquote_plus(s3_info['object']['key'], encoding='utf-8')

    s3 = boto3.client('s3')
    print(boto3.__version__)
    file_hash = hashlib.md5()
    buffer_size = 20 * 1024 * 1024
    resp = s3.get_object(
        Bucket=bucket,
        Key=key
    )
    if resp["ContentLength"] > 40 * 1024 * 1024 * 1024:
        print(f"{key}: Too large to calculate, use a VPS instead.")
        return return_val(200)
    for chunk in resp["Body"].iter_chunks(chunk_size=buffer_size):
        file_hash.update(chunk)

    md5 = file_hash.hexdigest()
    tags = {tag['Key']: tag['Value'] for tag in s3.get_object_tagging(
        Bucket=bucket, Key=key
    )['TagSet']}
    tags['MD5'] = md5
    tags['archive'] = 'yes'
    s3.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={'TagSet': [{'Key': k, 'Value': v} for k, v in tags.items()]},
    )
    note = f"MD5 {md5} of {bucket}::{key} added to tags."
    print(note)
    return return_val(200, note)


def return_val(val, body=None):
    ret = {
        'statusCode': val
    }
    if body is not None:
        ret['body'] = body
    return ret
