import json
import boto3
import uuid
import os

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME")


def lambda_handler(event, context):
    try:
        file_id = str(uuid.uuid4())
        file_key = f"uploads/{file_id}.jpg"

        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": "image/jpeg"
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "upload_url": upload_url,
                "file_key": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }