import json
import boto3
import urllib.parse
import io
import os
from PIL import Image

s3 = boto3.client("s3")

SUPPORTED_FORMATS = ["jpg", "jpeg", "png"]
PROCESSING_MODES = {
    "thumbnail": {
        "size": (300, 300),
        "jpg_quality": 65
    },
    "web": {
        "size": (1200, 1200),
        "jpg_quality": 85
    },
    "hq": {
        "size": (1800, 1800),
        "jpg_quality": 90
    }
}


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

            if isinstance(body, str):
                body = json.loads(body)

            for s3_record in body["Records"]:
                process_s3_record(s3_record)

        except Exception as e:
            log("ERROR", "Processing SQS record failed", error=str(e))
            raise e

    return {"statusCode": 200}


def process_s3_record(s3_record):
    s3_info = s3_record["s3"]

    bucket = s3_info["bucket"]["name"]
    key = urllib.parse.unquote_plus(s3_info["object"]["key"])

    log("INFO", "Processing file", key=key)

    if not key.startswith("uploads/"):
        log("INFO", "Skipping non-upload file", key=key)
        return

    if key.startswith("processed/"):
        log("INFO", "Skipping already processed file", key=key)
        return

    ext = key.split(".")[-1].lower()

    if ext not in SUPPORTED_FORMATS:
        log("WARN", "Unsupported file type", extension=ext)
        return

    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()
    
    metadata = response.get("Metadata", {})
    mode = metadata.get("mode", "web")
    
    if mode not in PROCESSING_MODES:
        mode = "web"
        
    settings = PROCESSING_MODES[mode]
    
    log("INFO", "Processing mode selected", mode=mode)

    try:
        image = Image.open(io.BytesIO(image_content))
    except Exception:
        log("ERROR", "Invalid image file", key=key)
        return

    original_size = len(image_content)

    # Resize according to selected mode
    image.thumbnail(settings["size"])

    buffer = io.BytesIO()

    if ext in ["jpg", "jpeg"]:
        image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=settings["jpg_quality"], optimize=True)
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

    log(
        "INFO",
        "File processed successfully",
        input_key=key,
        output_key=new_key,
        original_size=original_size,
        new_size=len(buffer.getvalue())
    )