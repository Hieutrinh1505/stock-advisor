import boto3 
from dotenv import load_dotenv
from botocore.client import Config
from botocore.exceptions import ClientError
import os 
load_dotenv()

class S3Storage:
    def __init__(self):
        # Use localhost when accessing from host machine
        self.endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000/browser")
        self.access_key_id = os.environ.get("MINIO_USERNAME", "minioadmin")
        self.access_key = os.environ.get("MINIO_PASSWORD", "minioadmin")
        # Remove region_name or set to empty string for MinIO
        self.config = Config(signature_version="s3v4")
    
    def get_client(self) -> boto3.client:
        return boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key,
            config=self.config
            # No region_name needed for MinIO
        )

    def list_buckets(self):
        s3_client = self.get_client()
        try:
            response = s3_client.list_buckets()
            print(f"✓ Connected to: {self.endpoint_url}")
            print(f"Buckets found: {len(response['Buckets'])}")
            for bucket in response['Buckets']:
                print(f"  - {bucket['Name']}")
            return response['Buckets']
        except Exception as e:
            print(f"Error: {e}")
            return []

if __name__ == "__main__":
    storage = S3Storage()
    storage.list_buckets()