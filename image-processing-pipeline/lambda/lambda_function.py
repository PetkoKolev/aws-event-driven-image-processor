import json
import boto3
from PIL import Image
import io
import urllib.parse

s3 = boto3.client("s3")

def lambda_handler(event, context):
    print("RAW EVENT:", json.dumps(event))

    if "Records" not in event:
        print("No Records in event")
        return {"statusCode": 200}

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])

            # 🧠 Skip test events
            if "Records" not in body:
                print("Skipping non-S3 event:", body)
                continue

            s3_info = body["Records"][0]["s3"]

            bucket = s3_info["bucket"]["name"]
            key = urllib.parse.unquote_plus(s3_info["object"]["key"])

            print(f"Processing file: {key}")

            # ❗ Avoid reprocessing
            if key.startswith("processed-"):
                print("Skipping already processed file")
                continue

            # Get image
            response = s3.get_object(Bucket=bucket, Key=key)
            image_content = response["Body"].read()

            image = Image.open(io.BytesIO(image_content))
            image = image.resize((300, 300))

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            new_key = f"processed-{key.split('/')[-1]}"

            s3.put_object(
                Bucket=bucket,
                Key=new_key,
                Body=buffer,
                ContentType="image/jpeg"
            )

            print(f"Created: {new_key}")

        except Exception as e:
            print("ERROR:", str(e))

    return {"statusCode": 200}