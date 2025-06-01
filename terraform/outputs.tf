
# terraform/outputs.tf
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.spark_data.bucket
}

output "car_models_path" {
  description = "S3 path for car models"
  value       = "s3a://${aws_s3_bucket.spark_data.bucket}/data/dims/car_models/"
}

output "car_colors_path" {
  description = "S3 path for car colors"  
  value       = "s3a://${aws_s3_bucket.spark_data.bucket}/data/dims/car_colors/"
}

output "cars_path" {
  description = "S3 path for cars"
  value       = "s3a://${aws_s3_bucket.spark_data.bucket}/data/dims/cars/"
}

output "emr_cluster_id" {
  description = "EMR cluster ID"
  value       = module.emr.cluster_id
}

output "emr_cluster_state" {
  description = "EMR cluster state"  
  value       = module.emr.cluster_state
}

output "emr_master_dns" {
  description = "EMR master node DNS"
  value       = module.emr.master_public_dns
}
