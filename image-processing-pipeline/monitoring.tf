# =========================
# SNS Topic for Alerts
# =========================
resource "aws_sns_topic" "alerts" {
  name = "image-processing-alerts"
}

# =========================
# Email Subscription
# =========================
resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "petkokolev00@icloud.com"
}

# =========================
# Image Processor Lambda Error Alarm
# =========================
resource "aws_cloudwatch_metric_alarm" "image_processor_errors" {
  alarm_name          = "image-processor-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alarm when image processor Lambda errors"

  dimensions = {
    FunctionName = aws_lambda_function.image_processor.function_name
  }

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]
}

# =========================
# API Lambda Error Alarm
# =========================
resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "image-api-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alarm when API Lambda errors"

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]
}

# =========================
# DLQ Queue Depth Alarm
# =========================
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "image-processing-dlq-messages"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1
  alarm_description   = "Alarm when DLQ contains failed messages"

  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]
}