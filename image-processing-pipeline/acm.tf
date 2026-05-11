resource "aws_acm_certificate" "frontend" {
  provider = aws.us_east_1

  domain_name       = "ipp.petkokolev-cloud.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}