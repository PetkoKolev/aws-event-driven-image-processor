terraform {
  backend "s3" {
    bucket         = "petko-terraform-state-image"
    key            = "image-processor/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "eu-west-2"
}