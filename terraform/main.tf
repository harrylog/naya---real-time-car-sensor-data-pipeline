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

# MSK Module
module "msk" {
  source = "./modules/msk"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region
  
  tags = var.tags
}

# Output MSK connection info for easy access
output "msk_connection_info" {
  description = "MSK cluster connection information"
  value = {
    cluster_name      = module.msk.cluster_name
    bootstrap_servers = module.msk.bootstrap_brokers
    topics_needed     = ["sensors-sample", "samples-enriched", "alert-data"]
  }
  sensitive = false
}
