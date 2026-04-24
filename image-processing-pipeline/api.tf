# =========================
# API Lambda
# =========================
resource "aws_lambda_function" "api" {
  function_name = "image-upload-api"

  filename         = "${path.module}/../backend/api/function.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/api/function.zip")

  handler = "handler.lambda_handler"
  runtime = "python3.11"

  role = aws_iam_role.lambda_role.arn

  timeout = 10

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.bucket
    }
  }
}

# =========================
# Allow API Gateway → Lambda
# =========================
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
}

# =========================
# API Gateway
# =========================
resource "aws_apigatewayv2_api" "api" {
  name          = "image-upload-api"
  protocol_type = "HTTP"
}

# =========================
# Integration (API → Lambda)
# =========================
resource "aws_apigatewayv2_integration" "api_lambda" {
  api_id = aws_apigatewayv2_api.api.id

  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api.invoke_arn
}

# =========================
# Route
# =========================
resource "aws_apigatewayv2_route" "upload" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /upload"

  target = "integrations/${aws_apigatewayv2_integration.api_lambda.id}"
}

# =========================
# Stage
# =========================
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}