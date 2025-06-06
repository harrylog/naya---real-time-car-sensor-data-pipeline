variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "spark-kafka-pipeline"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "spark-kafka-pipeline"
    Environment = "dev"
    Purpose     = "learning-data-engineering"
  }
}
