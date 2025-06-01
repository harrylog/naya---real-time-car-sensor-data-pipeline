variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name for EMR"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EMR cluster"
  type        = string
  default     = null
}

variable "instance_type" {
  description = "EC2 instance type for EMR"
  type        = string
  default     = "m5.xlarge"  # Cost-optimized
}

variable "instance_count" {
  description = "Number of instances in EMR cluster"
  type        = number
  default     = 1  # Single node for cost savings
}
