import json
import boto3
import uuid
import os

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME")

ALLOWED_TYPES = ["image/jpeg", "image/png"]


def lambda_handler(event, context):
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method")

        # HANDLE CORS PREFLIGHT
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": ""
            }

        headers = event.get("headers", {}) or {}
        content_type = headers.get("content-type", "image/jpeg")

        # Validate type
        if content_type not in ALLOWED_TYPES:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Invalid file type"})
            }

        # Determine extension
        if content_type == "image/png":
            extension = "png"
        else:
            extension = "jpg"

        file_id = str(uuid.uuid4())
        file_key = f"uploads/{file_id}.{extension}"

        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": content_type
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "upload_url": upload_url,
                "file_key": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }