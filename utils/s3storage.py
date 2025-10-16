import boto3 
from dotenv import load_dotenv
from botocore.client import Config
from botocore.exceptions import ClientError
import os 
from pathlib import Path

load_dotenv()

class S3Storage:
    """S3/MinIO storage client for file operations."""

    def __init__(self):
        """Initialize S3 client configuration."""
        self.endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
        self.access_key_id = os.environ.get("MINIO_USERNAME", "minioadmin")
        self.access_key = os.environ.get("MINIO_PASSWORD", "minioadmin")
        self.config = Config(signature_version="s3v4")
    
    def get_client(self) -> boto3.client:
        """Create and return S3 client."""
        return boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key,
            config=self.config
        )

    def list_buckets(self):
        """List all available S3 buckets."""
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
    
    def upload_file(self, folder_path: str, bucket_name: str, object_name=None):
        """Upload parquet files from a folder to S3/MinIO bucket.

        Args:
            folder_path: Path to folder containing parquet files
            bucket_name: Target S3/MinIO bucket name
            object_name: S3 prefix/path (required)
        """
        if object_name is None:
            print("Please specify your path")
            return
        
        s3_client = self.get_client()
        data_path = Path(folder_path)

        if not data_path.exists():
            print(f"Error: Folder '{folder_path}' does not exist")
            return

        # Find all parquet files in folder
        parquet_files = list(data_path.glob('*.parquet'))
        
        if not parquet_files:
            print(f"No parquet files found in '{folder_path}'")
            return
        
        print(f"Found {len(parquet_files)} parquet file(s)")
        
        for file_path in parquet_files:
            filename = file_path.name
            s3_key = f"{object_name}/{filename}"
            
            try:
                print(f"Uploading {filename} to s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key
                )
                print(f"✓ Successfully uploaded {filename}")
            except Exception as e:
                print(f"✗ Error uploading {filename}: {str(e)}")
        
        print("Upload complete!")

if __name__ == "__main__":
    storage = S3Storage()
    storage.list_buckets()
    storage.upload_file(
        folder_path="data",
        bucket_name="stocks",
        object_name="history"
    )