# EMR Service Role with full admin access
resource "aws_iam_role" "emr_service_role" {
  name = "${var.project_name}-emr-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticmapreduce.amazonaws.com"
        }
      }
    ]
  })
}

# Give EMR service role full admin access
resource "aws_iam_role_policy_attachment" "emr_service_admin" {
  role       = aws_iam_role.emr_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# EMR EC2 Instance Role with full admin access
resource "aws_iam_role" "emr_instance_role" {
  name = "${var.project_name}-emr-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Give EMR instances full admin access
resource "aws_iam_role_policy_attachment" "emr_instance_admin" {
  role       = aws_iam_role.emr_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# Instance Profile
resource "aws_iam_instance_profile" "emr_profile" {
  name = "${var.project_name}-emr-instance-profile"
  role = aws_iam_role.emr_instance_role.name
}