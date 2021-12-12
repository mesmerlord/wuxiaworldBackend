from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False

class ThumbnailStorage(S3Boto3Storage):
    location = 'media/thumbnail'
    default_acl = 'public-read'
    file_overwrite = False


class FullStorage(S3Boto3Storage):
    location = 'media/full'
    default_acl = 'public-read'
    file_overwrite = False

class OriginalStorage(S3Boto3Storage):
    location = 'media/original'
    default_acl = 'public-read'
    file_overwrite = False