output "cluster_id" {
  description = "EMR cluster ID"
  value       = aws_emr_cluster.spark_cluster.id
}

output "cluster_name" {
  description = "EMR cluster name"
  value       = aws_emr_cluster.spark_cluster.name
}

output "master_public_dns" {
  description = "EMR master node public DNS"
  value       = aws_emr_cluster.spark_cluster.master_public_dns
}

output "cluster_state" {
  description = "EMR cluster state"
  value       = aws_emr_cluster.spark_cluster.cluster_state
}
