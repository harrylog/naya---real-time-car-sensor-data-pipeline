data "aws_vpcs" "available" {}

data "aws_vpc" "selected" {
  id = data.aws_vpcs.available.ids[0]
}

data "aws_subnets" "available" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# Create EC2 Key Pair for EMR
resource "aws_key_pair" "emr_key" {
  key_name   = "${var.project_name}-emr-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCz7rsMJZfvGXMQp+WWCMHdnEWchG5VisfCcTFlX1gUGvs/JZHpg+Gd4A594yS191S/p9E5ErW2agyoMNWNK5X13JLGWWCNHo4gU9HhVNi3LvmuBukRqyZG71zxIlaZKZzDJT6aroA+NzFv1+B3l/HVGMfHaSb7hY+/XgXbhqd0Gae2zLjzzTRzryLPgphQcAXRU3CDQhrKaDRSfCGWpWa8Y8R5edovmxhIGVU58MsrpRQ4G9EA1W6NxlFoGeZZdFkZrwQDIr/ysVcDPDsdYQSKFouNNnb6SDwDyxZppuPzBqLsTQt2woEgKRHCeF31XbA8oZm7BNXmfTSX+CExTqazJVJ3+IdNXfxX8dgkfEaAeAHqb7e/GtOPwd26tqo02uhkJJzXneJ8Vjycy31JSFxMso+/m3ImcltP+oTl2i3/Fke5YI23hzkq0+Khj/UggCX26l1XIzRnmG2RoF8IOp6JPK8yiNiOuvGEAEYJuUdgUbW2/ph3QmsrpWsI8qTStUrCwKsl1ugpXJKREfbtIhM1Bhk+vlqPEW65GZLMDy0fEcUh3xoY1dqdmWGAsNSO56WKJjWBCFThWwu1jlcC+sd9Gek0fAfi8uLWVn9lmp9SOKq1hWdPJDTyAczNe+FwbDkMnAik1BpTAjgvHX/4mu58UImBtD69DvkWBn2l2kQZKQ== harry@harry-Latitude-5550"  
  
  lifecycle {
    ignore_changes = [public_key]
  }
}

# Security Group for EMR
resource "aws_security_group" "emr_master" {
  name_prefix = "${var.project_name}-emr-master"
  vpc_id      = data.aws_vpc.selected.id

  # SSH access (if needed for debugging)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict this in production
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-emr-master-sg"
  }
}

# EMR Cluster
resource "aws_emr_cluster" "spark_cluster" {
  name          = "${var.project_name}-cluster"
  release_label = "emr-6.15.0"
  applications  = ["Spark"]

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true  # Keep cluster running for multiple jobs

ec2_attributes {
  key_name         = aws_key_pair.emr_key.key_name
  subnet_id        = var.subnet_id != null ? var.subnet_id : data.aws_subnets.available.ids[0]  # Change "default" to "available"
  instance_profile = aws_iam_instance_profile.emr_profile.arn
}

  master_instance_group {
    instance_type = var.instance_type
  }

  # Single node cluster (master only)
  # core_instance_group {
  #   instance_type  = var.instance_type
  #   instance_count = var.instance_count
  # }

  service_role = aws_iam_role.emr_service_role.arn

  log_uri = "s3://${var.bucket_name}/logs/emr/"

  tags = {
    Name        = "${var.project_name}-emr-cluster"
    Environment = "dev"
    Project     = var.project_name
  }
}
