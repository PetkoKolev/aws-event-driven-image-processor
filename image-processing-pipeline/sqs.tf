# Dead Letter Queue (for failed messages)
resource "aws_sqs_queue" "dlq" {
  name = "image-processing-dlq"
}

# Main processing queue
resource "aws_sqs_queue" "image_queue" {
  name = "image-processing-queue"

  # Important: must be >= Lambda execution timeout
  visibility_timeout_seconds = 30

  # DLQ configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}

# Allow S3 to send messages to SQS
resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.image_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.image_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.images.arn
          }
        }
      }
    ]
  })
}