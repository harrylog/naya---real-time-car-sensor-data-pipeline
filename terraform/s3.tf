# Create unique bucket name
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "spark_data" {
  bucket = "${var.project_name}-${random_string.bucket_suffix.result}"
}

resource "aws_s3_object" "car_models_csv" {
  bucket = aws_s3_bucket.spark_data.id
  key    = "data/dims/car_models/car_models.csv"
  
  content = <<-EOT
model_id,car_brand,car_model
1,Mazda,3
2,Mazda,6
3,Toyota,Corolla
4,Hyundai,i20
5,Kia,Sportage
6,Kia,Rio
7,Kia,Picanto
EOT

  content_type = "text/csv"
}

# Upload car colors CSV data
resource "aws_s3_object" "car_colors_csv" {
  bucket = aws_s3_bucket.spark_data.id
  key    = "data/dims/car_colors/car_colors.csv"
  
  content = <<-EOT
color_id,color_name
1,Black
2,Red
3,Gray
4,White
5,Green
6,Blue
7,Pink
EOT

  content_type = "text/csv"
}

# Create empty folder for cars (will be populated by PySpark later)
resource "aws_s3_object" "cars_folder" {
  bucket = aws_s3_bucket.spark_data.id
  key    = "data/dims/cars/.keep"
  content = ""
}

