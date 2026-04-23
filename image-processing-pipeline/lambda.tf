resource "aws_lambda_function" "image_processor" {
  function_name = "image-processor"

  filename         = "lambda/function.zip"
  source_code_hash = filebase64sha256("lambda/function.zip")

  handler = "lambda_function.lambda_handler"
  runtime = "python3.11"

  role = aws_iam_role.lambda_role.arn

  timeout = 10
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.image_queue.arn
  function_name    = aws_lambda_function.image_processor.arn

  batch_size = 1
}

resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_processor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.image_queue.arn
}