import logging
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from fastapi import UploadFile
from src.aws.utils import generate_object_name
from src.config import settings


class S3Client:
    def __init__(
        self, 
        access_key: str = settings.S3_ACCESS_KEY_ID,
        secret_key: str = settings.S3_SECRET_ACCESS_KEY,
        endpoint_url: str = settings.S3_ENDPOINT_URL,
        bucket_name: str = settings.S3_BUCKET_NAME,
    ):
        self.config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint_url
        }
        self.bucket_name = bucket_name
        self.session = get_session()
    
    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client('s3', **self.config) as client:
            yield client
    
    async def upload_file(self, file: UploadFile) -> str:
        object_name = generate_object_name(file.filename)
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file.file
            )
            
        logging.getLogger('aws_logger').info(f'Upload file with name: {object_name}')
        return f'{self.bucket_name}/{object_name}'
    