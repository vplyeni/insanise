from storages.backends.s3boto3 import S3Boto3Storage


class HarmoniseS3Boto3Storage(S3Boto3Storage):
    location = "harmonise"
    default_acl = "private"
    file_overwrite = False