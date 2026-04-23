resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_s3_bucket" "images" {
  bucket = "petko-image-upload-${random_id.bucket_id.hex}"
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.images.id

  queue {
    queue_arn = aws_sqs_queue.image_queue.arn
    events    = ["s3:ObjectCreated:*"]

    filter_prefix = "uploads/"
  }

  depends_on = [aws_sqs_queue_policy.allow_s3]
}