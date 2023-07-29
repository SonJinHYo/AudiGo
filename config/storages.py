from storages.backends.s3boto3 import S3Boto3Storage


__all__ = (
    "StaticStorage",
    "MediaStorage",
)


# 정적 파일용
class StaticStorage(S3Boto3Storage):
    default_acl = "public-read"
    location = "static"


# 미디어 파일용
class MediaStorage(S3Boto3Storage):
    location = "audio"
    default_acl = "public-read"
