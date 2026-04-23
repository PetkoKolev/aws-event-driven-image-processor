# AWS Event-Driven Image Processing Pipeline

An event-driven image processing system built using AWS services and Terraform.

## Architecture

- **S3** – stores uploaded images
- **SQS** – queues events from S3
- **Lambda** – processes images asynchronously
- **Terraform** – provisions infrastructure

Flow:
1. Image uploaded to S3
2. Event sent to SQS
3. Lambda triggered from SQS
4. Image processed in Lambda

---

##  Project Structure

backend/
├── api/
└── worker/

image-processing-pipeline/
├── lambda/
│   └── lambda_function.py
├── iam.tf
├── lambda.tf
├── s3.tf
├── sqs.tf
└── provider.tf

terraform/ (legacy setup)

---

## Infrastructure

Provisioned using Terraform:

- S3 bucket for uploads
- SQS queue for event handling
- Lambda function for processing
- IAM roles and permissions

---

## Current Status

- ✅ S3 → SQS event flow working
- ✅ Lambda deployed via Terraform
- ⚠️ Image processing logic basic (in progress)
- ⚠️ No CI/CD yet

---

## Next Steps

- Improve image processing logic from thumbnail and very compressed to having more options such as picture rotation settings via EXIF)
- Add DynamoDB for metadata storage
- Implement CI/CD pipeline
- Add API layer

---

## Tech Stack

- AWS (S3, SQS, Lambda)
- Terraform
- Python
