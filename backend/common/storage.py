import os
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
import shutil
from pathlib import Path
import uuid

class BaseStorage(ABC):
    @abstractmethod
    def save(self, file_obj, filename: str) -> str:
        pass

    @abstractmethod
    def get_url(self, storage_key: str) -> str:
        pass

    @abstractmethod
    def read(self, storage_key: str) -> bytes:
        pass

class MockStorage(BaseStorage):
    def __init__(self):
        self.storage_dir = Path(settings.BASE_DIR) / 'local_storage'
        self.storage_dir.mkdir(exist_ok=True)

    def save(self, file_obj, filename: str) -> str:
        key = f"{uuid.uuid4()}-{filename}"
        dest_path = self.storage_dir / key
        
        file_obj.seek(0)
        with open(dest_path, 'wb') as f:
            f.write(file_obj.read())
            
        return key

    def get_url(self, storage_key: str) -> str:
        # In a real app, this would be a local view serving the file
        return f"/api/documents/local/{storage_key}"

    def read(self, storage_key: str) -> bytes:
        path = self.storage_dir / storage_key
        if not path.exists():
            raise FileNotFoundError(f"File not found: {storage_key}")
        with open(path, 'rb') as f:
            return f.read()

class S3Storage(BaseStorage):
    def __init__(self):
        self.bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME', 'us-east-1'),
            endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL', None)
        )

    def save(self, file_obj, filename: str) -> str:
        key = f"{uuid.uuid4()}-{filename}"
        file_obj.seek(0)
        self.s3.upload_fileobj(file_obj, self.bucket, key)
        return key

    def get_url(self, storage_key: str) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': storage_key},
            ExpiresIn=3600
        )

    def read(self, storage_key: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=storage_key)
            return response['Body'].read()
        except ClientError as e:
            raise FileNotFoundError(f"S3 Error: {e}")

def get_storage_client() -> BaseStorage:
    if getattr(settings, 'USE_MOCK_STORAGE', False):
        return MockStorage()
    return S3Storage()
