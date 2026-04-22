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

resource "aws_sqs_queue" "image_queue" {
  name = "image-processing-queue"
}

output "bucket_name" {
  value = aws_s3_bucket.images.bucket
}

output "queue_url" {
  value = aws_sqs_queue.image_queue.id
}