from google.cloud import storage
from django.conf import settings

def upload_file(bucket_name, file_stream, destination_blob_name):
    storage_client = storage.Client(project=settings.GCP_PROJECT)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_stream)