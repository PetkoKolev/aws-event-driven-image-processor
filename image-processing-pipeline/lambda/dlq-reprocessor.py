import json
import boto3

sqs = boto3.client("sqs")

QUEUE_URL = "YOUR_MAIN_QUEUE_URL"  # replace


def log(level, message, **kwargs):
    print(json.dumps({
        "level": level,
        "message": message,
        **kwargs
    }))


def lambda_handler(event, context):
    log("INFO", "DLQ reprocessor triggered", raw_event=event)

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])

            retry_count = body.get("retry_count", 0)

            if retry_count >= 3:
                log("WARN", "Max retries reached, dropping message", retry_count=retry_count)
                continue

            body["retry_count"] = retry_count + 1

            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(body)
            )

            log("INFO", "Message requeued", retry_count=body["retry_count"])

        except Exception as e:
            log("ERROR", "Failed to process DLQ message", error=str(e))
            raise e

    return {"statusCode": 200}