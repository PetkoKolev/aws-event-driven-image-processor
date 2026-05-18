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