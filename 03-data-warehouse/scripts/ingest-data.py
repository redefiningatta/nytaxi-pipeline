#!/usr/bin/env python3
"""
Load Yellow Taxi data (Jan-Jun 2024) to GCS bucket
"""

import requests
from pathlib import Path
from google.cloud import storage
import os

# Configuration
BUCKET_NAME = "nytaxi-485607-yellow_taxi"  # Your bucket name
PROJECT_ID = "nytaxi-485607"
MONTHS = ["01", "02", "03", "04", "05", "06"]
YEAR = "2024"
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

def download_file(url: str, local_path: Path) -> bool:
    """Download file from URL to local path"""
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded to {local_path}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def upload_to_gcs(local_path: Path, bucket_name: str, blob_name: str):
    """Upload file to GCS bucket"""
    print(f"Uploading {local_path} to gs://{bucket_name}/{blob_name}...")
    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(str(local_path))
        print(f"✓ Uploaded to gs://{bucket_name}/{blob_name}")
        return True
    except Exception as e:
        print(f"✗ Error uploading to GCS: {e}")
        return False

def main():
    # Create local data directory
    data_dir = Path("data/yellow_taxi")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading Yellow Taxi data for {YEAR} (Jan-Jun) to GCS bucket: {BUCKET_NAME}\n")
    
    success_count = 0
    
    for month in MONTHS:
        filename = f"yellow_tripdata_{YEAR}-{month}.parquet"
        url = f"{BASE_URL}/{filename}"
        local_path = data_dir / filename
        
        # Download file
        if download_file(url, local_path):
            # Upload to GCS
            if upload_to_gcs(local_path, BUCKET_NAME, f"raw/{filename}"):
                success_count += 1
                # Clean up local file to save space
                local_path.unlink()
            else:
                print(f"Failed to upload {filename}")
        else:
            print(f"Failed to download {filename}")
        
        print()  # Blank line between files
    
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(MONTHS)} files successfully uploaded to GCS")
    print(f"{'='*60}")
    
    # List files in bucket to verify
    print(f"\nFiles in gs://{BUCKET_NAME}/raw/:")
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix="raw/")
    for blob in blobs:
        print(f"  - {blob.name}")

if __name__ == "__main__":
    main()
