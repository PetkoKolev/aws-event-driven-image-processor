import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]

ALLOWED_TYPES = {"image/jpeg", "image/png"}
ALLOWED_MODES = {"thumbnail", "web", "hq"}


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "https://ipp.petkokolev-cloud.com",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
            or event.get("httpMethod")
        )

        # =========================
        # HANDLE CORS PREFLIGHT
        # =========================
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "https://ipp.petkokolev-cloud.com",
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
                return build_response(400, {"error": "Missing key"})

            filename = original_key.split("/")[-1]
            processed_key = f"processed/resized-{filename}"

            try:
                s3.head_object(
                    Bucket=BUCKET_NAME,
                    Key=processed_key
                )

            except ClientError as e:
                error_code = e.response["Error"]["Code"]

                if error_code in ("404", "NoSuchKey", "403", "AccessDenied"):
                    return build_response(404, {"error": "Not ready yet"})

                raise

            image_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": processed_key,
                    "ResponseContentDisposition": f'attachment; filename="processed-{filename}"'
                },
                ExpiresIn=3600
            )

            return build_response(200, {
                "image_url": image_url
            })

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

        if content_type not in ALLOWED_TYPES:
            return build_response(400, {
                "error": "Invalid file type. Only JPEG and PNG are allowed."
            })

        if mode not in ALLOWED_MODES:
            return build_response(400, {
                "error": "Invalid processing mode."
            })

        extension = "png" if content_type == "image/png" else "jpg"

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

        return build_response(200, {
            "upload_url": upload_url,
            "file_key": file_key
        })

    except Exception as e:
        print(f"API error: {str(e)}")

        return build_response(500, {
            "error": "Internal server error"
        })