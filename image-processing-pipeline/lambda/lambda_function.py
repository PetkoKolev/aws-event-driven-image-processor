import json
import boto3
from PIL import Image
import io
import urllib.parse
import os

s3 = boto3.client("s3")

SUPPORTED_FORMATS = ("jpg", "jpeg", "png")


def lambda_handler(event, context):
    print("[INFO] RAW EVENT:", json.dumps(event))

    if "Records" not in event:
        print("[WARN] No Records in event")
        return {"statusCode": 200}

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])

            if "Records" not in body:
                print("[WARN] Skipping non-S3 event:", body)
                continue

            for s3_record in body["Records"]:
                process_s3_record(s3_record)

        except Exception as e:
            print("[ERROR] Processing SQS record failed:", str(e))
            raise e #Required for retries + DLQ

    return {"statusCode": 200}


def process_s3_record(s3_record):
    s3_info = s3_record["s3"]

    bucket = s3_info["bucket"]["name"]
    key = urllib.parse.unquote_plus(s3_info["object"]["key"])

    print(f"[INFO] Processing file: {key}")

    # DLQ TEST: force failure if filename contains "fail"
    if "fail" in key:
        print("[TEST] Forced failure triggered")
        raise Exception("Forced failure for DLQ testing")

    # ONLY process uploads/ folder
    if not key.startswith("uploads/"):
        print("[INFO] Skipping non-upload file")
        return

    # Skip already processed files
    if key.startswith("processed/"):
        print("[INFO] Skipping already processed file")
        return

    # Validate extension
    ext = key.split(".")[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        print(f"[WARN] Unsupported file type: {ext}")
        return

    # Get object
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()

    # Open safely
    try:
        image = Image.open(io.BytesIO(image_content))
    except Exception:
        print("[ERROR] Invalid image file")
        return

    # Resize (maintain aspect ratio)
    image.thumbnail((300, 300))

    buffer = io.BytesIO()

    if ext in ("jpg", "jpeg"):
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

    # Improved naming
    new_key = f"processed/resized-{name}.{new_ext}"

    s3.put_object(
        Bucket=bucket,
        Key=new_key,
        Body=buffer,
        ContentType=content_type
    )

    print(f"[SUCCESS] Created: {new_key}")