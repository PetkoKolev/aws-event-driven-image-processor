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

## Event Flow

1. User uploads image to `uploads/` folder in S3
2. S3 emits event notification
3. Event is sent to SQS queue
4. Lambda polls SQS and processes image
5. Processed image is stored in `processed/` folder

### Folder Structure Logic

- `uploads/` → incoming raw images
- `processed/` → transformed output images

This separation prevents recursive processing and ensures clean data flow. - AWS flagged during testing which helped stop high costs from incurring.

---

##  Project Structure

```bash
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
```

---

## Infrastructure

Provisioned using Terraform:

- S3 bucket for uploads
- SQS queue for event handling
- Lambda function for processing
- IAM roles and permissions

---

## Current Status

- ✅ Fully working event-driven pipeline (S3 → SQS → Lambda → S3)
- ✅ Image resizing with format handling (JPG, PNG)
- ✅ Safe processing using folder-based filtering
- ✅ Production-compatible dependency packaging
- ⚠️ CI/CD pipeline not yet implemented

---

## Challenges & Solutions

### Lambda Dependency Issues
- Encountered `_imaging` import errors with Pillow
- Root cause: dependencies built on macOS (incompatible with AWS Lambda Linux runtime)
- Solution: packaged dependencies using Docker with Lambda-compatible environment

### Architecture Mismatch
- Initial builds failed due to ARM vs x86 incompatibility
- Fixed by using correct Lambda base image during packaging

### Event Filtering
- Ensured only `uploads/` folder triggers processing
- Prevents infinite loops and unintended executions

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
