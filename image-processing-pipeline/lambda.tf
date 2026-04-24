# =========================
# Image Processor Lambda
# =========================
resource "aws_lambda_function" "image_processor" {
  function_name = "image-processor"

  filename         = "${path.module}/image_processor.zip"
  source_code_hash = filebase64sha256("${path.module}/image_processor.zip")

  handler = "lambda_function.lambda_handler"
  runtime = "python3.11"

  role = aws_iam_role.lambda_role.arn

  timeout = 10
}

# =========================
# DLQ Reprocessor Lambda
# =========================
resource "aws_lambda_function" "dlq_reprocessor" {
  function_name = "dlq-reprocessor"

  filename         = "${path.module}/dlq_reprocessor.zip"
  source_code_hash = filebase64sha256("${path.module}/dlq_reprocessor.zip")

  handler = "lambda_function.lambda_handler"
  runtime = "python3.11"

  role = aws_iam_role.lambda_role.arn

  timeout = 10
}

# =========================
# SQS → Image Processor
# =========================
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.image_queue.arn
  function_name    = aws_lambda_function.image_processor.arn

  batch_size = 1
}

# =========================
# SQS → DLQ Reprocessor
# =========================
resource "aws_lambda_event_source_mapping" "dlq_trigger" {
  event_source_arn = aws_sqs_queue.dlq.arn
  function_name    = aws_lambda_function.dlq_reprocessor.arn

  batch_size = 1
}

# =========================
# Permissions (Image Processor)
# =========================
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_processor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.image_queue.arn
}

# =========================
# Permissions (DLQ Reprocessor)
# =========================
resource "aws_lambda_permission" "allow_dlq" {
  statement_id  = "AllowExecutionFromDLQ"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dlq_reprocessor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.dlq.arn
}