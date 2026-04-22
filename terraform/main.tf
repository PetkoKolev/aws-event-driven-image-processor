provider "aws" {
  region = "eu-west-2"
}

resource "aws_s3_bucket" "images" {
  bucket = "petko-image-upload-${random_id.suffix.hex}"

  force_destroy = true
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.images.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.images.id

  queue {
    queue_arn = aws_sqs_queue.image_queue.arn
    events    = ["s3:ObjectCreated:*"]
  }
}

resource "aws_sqs_queue" "image_queue" {
  name = "image-processing-queue"
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.image_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
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

output "bucket_name" {
  value = aws_s3_bucket.images.bucket
}

output "queue_url" {
  value = aws_sqs_queue.image_queue.id
}