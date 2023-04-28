# while True:
#     resp = s3.get_object(
#         Bucket=bucket,
#         Key=key,
#         PartNumber=part_number
#     )
#     # print("received a part")
#     for chunk in resp["Body"].iter_chunks(chunk_size=buffer_size):
#         file_hash.update(chunk)
#     if part_number >= resp.get("PartsCount", 1):
#         break
#     part_number += 1