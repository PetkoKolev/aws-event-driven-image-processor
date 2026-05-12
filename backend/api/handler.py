import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME")

ALLOWED_TYPES = ["image/jpeg", "image/png"]
ALLOWED_MODES = ["thumbnail", "web", "hq"]


def lambda_handler(event, context):
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method") \
            or event.get("httpMethod")
            
        # =========================
        # HANDLE CORS PREFLIGHT
        # =========================
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": ""
            }

        # =========================
        # HANDLE GET (FETCH IMAGE)
        # =========================
        if method == "GET":
            params = event.get("queryStringParameters") or {}
            original_key = params.get("key")

            if not original_key:
                return {
                    "statusCode": 400,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "Missing key"})
                }

            # Convert uploads/xyz.jpg → processed/resized-xyz.jpg
            filename = original_key.split("/")[-1]
            processed_key = f"processed/resized-{filename}"

            # Check the processed file actually exists before generating a URL.
            # Without this, S3 returns 403 on the presigned URL when the object
            # isn't there yet, which the frontend can't distinguish from a real
            # permissions error.
            try:
                s3.head_object(Bucket=BUCKET_NAME, Key=processed_key)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code in ("404", "NoSuchKey", "403", "AccessDenied"):
                    return {
                        "statusCode": 404,
                        "headers": {"Access-Control-Allow-Origin": "*"},
                        "body": json.dumps({"error": "Not ready yet"})
                    }
                raise

            # Generate signed GET URL
            image_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": processed_key,
                    "ResponseContentDisposition": f'attachment; filename="processed-{filename}"'
                },
                ExpiresIn=3600
            )

            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "image_url": image_url
                })
            }

        # =========================
        # HANDLE POST (UPLOAD)
        # =========================
        headers = event.get("headers", {}) or {}
        params = event.get("queryStringParameters") or {}
        mode = params.get("mode", "web")
        content_type = (
            headers.get("content-type")
            or headers.get("Content-Type")
            or ""
        ).split(";")[0]

        # Validate type
        if content_type not in ALLOWED_TYPES:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid file type"})
            }
            
        if mode not in ALLOWED_MODES:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid processing mode"})
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
                "ContentType": content_type,
                "Metadata": {
                    "mode": mode
                }
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "upload_url": upload_url,
                "file_key": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
