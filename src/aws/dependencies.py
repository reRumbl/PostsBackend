from typing import Annotated
from fastapi import Depends
from src.aws.client import S3Client


def get_s3_client():
    return S3Client()


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]
