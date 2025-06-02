# terraform/modules/msk/main.tf

# Data source to get VPC info - same approach as EMR
data "aws_vpcs" "available" {}
data "aws_vpc" "main" {
  id = data.aws_vpcs.available.ids[0]
}

data "aws_subnets" "available" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

# Security group for MSK cluster
resource "aws_security_group" "msk" {
  name_prefix = "${var.project_name}-msk-"
  vpc_id      = data.aws_vpc.main.id

  # Allow Kafka communication from EMR
  ingress {
    from_port   = 9092
    to_port     = 9098
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  # Allow Zookeeper communication
  ingress {
    from_port   = 2181
    to_port     = 2181
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-msk-sg"
    Project = var.project_name
  }
}

# CloudWatch log group for MSK logs (optional but helpful for debugging)
resource "aws_cloudwatch_log_group" "msk" {
  name              = "/aws/msk/${var.project_name}"
  retention_in_days = 3  # Keep costs low
  
  tags = {
    Project = var.project_name
  }
}

# MSK Configuration for cost optimization
resource "aws_msk_configuration" "main" {
  name           = "${var.project_name}-config"
  description    = "MSK configuration for ${var.project_name}"
  kafka_versions = ["2.8.1"]

  server_properties = <<EOF
# Cost optimization settings
auto.create.topics.enable=true
delete.topic.enable=true
log.retention.hours=1
log.retention.bytes=1073741824
log.segment.bytes=104857600
num.partitions=1
default.replication.factor=2
min.insync.replicas=1
EOF
}

# MSK Cluster - Minimum cost configuration
resource "aws_msk_cluster" "main" {
  cluster_name           = var.project_name
  kafka_version         = "2.8.1"
  number_of_broker_nodes = 2  # Minimum required

  broker_node_group_info {
    instance_type   = "kafka.t3.small"  # Smallest available
    client_subnets  = [
      data.aws_subnets.available.ids[0],
      data.aws_subnets.available.ids[1]
    ]
    storage_info {
      ebs_storage_info {
        volume_size = 10  # Minimum storage (GB)
      }
    }
    security_groups = [aws_security_group.msk.id]
  }

  # Basic encryption (required)
  encryption_info {
    encryption_in_transit {
      client_broker = "TLS_PLAINTEXT"  # Less secure but simpler for learning
      in_cluster    = true
    }
  }

  # Monitoring - minimal for cost savings
  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = false
      }
      node_exporter {
        enabled_in_broker = false
      }
    }
  }

  # Logging configuration
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk.name
      }
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.main.arn
    revision = aws_msk_configuration.main.latest_revision
  }

  tags = {
    Name        = "${var.project_name}-msk"
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "kafka-streaming-pipeline"
  }
}
