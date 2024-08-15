from storages.backends.s3boto3 import S3Boto3Storage


class HarmoniseS3Boto3Storage(S3Boto3Storage):
    location = "fields"
    default_acl = "public-read"
    file_overwrite = False
    bucket_name = "harmonise"
