import json
import boto3
import urllib.parse
import io
import os
from PIL import Image

s3 = boto3.client("s3")

SUPPORTED_FORMATS = ["jpg", "jpeg", "png"]


def log(level, message, **kwargs):
    print(json.dumps({
        "level": level,
        "message": message,
        **kwargs
    }))


def lambda_handler(event, context):
    log("INFO", "Lambda triggered", raw_event=event)

    for record in event["Records"]:
        try:
            body = record["body"]

            # Handle string vs dict body safely
            if isinstance(body, str):
                body = json.loads(body)

            for s3_record in body["Records"]:
                process_s3_record(s3_record)

        except Exception as e:
            log("ERROR", "Processing SQS record failed", error=str(e))
            raise e  # required for retries + DLQ

    return {"statusCode": 200}


def process_s3_record(s3_record):
    s3_info = s3_record["s3"]

    bucket = s3_info["bucket"]["name"]
    key = urllib.parse.unquote_plus(s3_info["object"]["key"])

    log("INFO", "Processing file", key=key)

    # Only process uploads/
    if not key.startswith("uploads/"):
        log("INFO", "Skipping non-upload file", key=key)
        return

    # Skip already processed
    if key.startswith("processed/"):
        log("INFO", "Skipping already processed file", key=key)
        return

    ext = key.split(".")[-1].lower()

    if ext not in SUPPORTED_FORMATS:
        log("WARN", "Unsupported file type", extension=ext)
        return

    # Get file
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()

    # Open safely
    try:
        image = Image.open(io.BytesIO(image_content))
    except Exception:
        log("ERROR", "Invalid image file", key=key)
        return

    # Resize
    image.thumbnail((300, 300))

    buffer = io.BytesIO()

    if ext in ["jpg", "jpeg"]:
        image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=85)
        content_type = "image/jpeg"
        new_ext = "jpg"

    elif ext == "png":
        image.save(buffer, format="PNG", optimize=True)
        content_type = "image/png"
        new_ext = "png"

    buffer.seek(0)

    filename = os.path.basename(key)
    name = filename.split(".")[0]

    new_key = f"processed/resized-{name}.{new_ext}"

    s3.put_object(
        Bucket=bucket,
        Key=new_key,
        Body=buffer,
        ContentType=content_type
    )

    log("INFO", "File processed successfully", output_key=new_key)