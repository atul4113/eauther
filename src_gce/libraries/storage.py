from google.cloud import storage


def upload_file_by_path(path, bucketname, blobname, type="application/zip"):
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucketname)
    blob = bucket.blob(blobname)
    blob.upload_from_filename(path, type)
