terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}


module "emr" {
  source = "./modules/emr"
  
  project_name = var.project_name
  bucket_name  = aws_s3_bucket.spark_data.bucket
}
