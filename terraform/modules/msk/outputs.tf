# terraform/modules/msk/outputs.tf

output "cluster_arn" {
  description = "ARN of the MSK cluster"
  value       = aws_msk_cluster.main.arn
}

output "cluster_name" {
  description = "Name of the MSK cluster"
  value       = aws_msk_cluster.main.cluster_name
}

output "zookeeper_connect_string" {
  description = "Zookeeper connection string"
  value       = aws_msk_cluster.main.zookeeper_connect_string
}

output "bootstrap_brokers" {
  description = "Plaintext connection host:port pairs"
  value       = aws_msk_cluster.main.bootstrap_brokers
}

output "bootstrap_brokers_tls" {
  description = "TLS connection host:port pairs"
  value       = aws_msk_cluster.main.bootstrap_brokers_tls
}

output "security_group_id" {
  description = "Security group ID for MSK cluster"
  value       = aws_security_group.msk.id
}

output "log_group_name" {
  description = "CloudWatch log group name for MSK"
  value       = aws_cloudwatch_log_group.msk.name
}

# For easy testing and connection from EMR
output "kafka_connection_info" {
  description = "Connection information for Kafka clients"
  value = {
    bootstrap_servers = aws_msk_cluster.main.bootstrap_brokers
    cluster_name      = aws_msk_cluster.main.cluster_name
    topics_to_create  = ["sensors-sample", "samples-enriched", "alert-data"]
  }
}
