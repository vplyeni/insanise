import os
import uuid

from storages.backends.s3boto3 import S3Boto3Storage


def get_new_name(name):
    # Generate a UUID for the new file name
    (_, ext) = os.path.splitext(name)
    new_name = f"{uuid.uuid4().hex}{ext}"
    return new_name


class HarmoniseS3Boto3Storage(S3Boto3Storage):
    location = "fields"
    default_acl = "public-read"
    file_overwrite = False
    bucket_name = "harmonise"

    def save(self, name, content, max_length=None):
        # Change the file name using UUID
        name = get_new_name(name)
        return super().save(name, content, max_length)
