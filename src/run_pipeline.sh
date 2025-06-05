#!/bin/bash
# run_pipeline.sh - Submit Spark jobs via EMR Steps

CLUSTER_ID="j-2SY25MZ9I0XIE"
S3_BUCKET="spark-kafka-pipeline-zn1fp2wf"  # Your bucket name

echo "🚀 Submitting Data Generator to EMR..."

# Submit Data Generator step
STEP_ID=$(aws emr add-steps --cluster-id $CLUSTER_ID --steps '[{
  "Name": "DataGenerator", 
  "ActionOnFailure": "CONTINUE",
  "Jar": "command-runner.jar",
  "Args": [
    "spark-submit",
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",
    "s3://'$S3_BUCKET'/scripts/data_generator.py"
  ]
}]' --query 'StepIds[0]' --output text)

echo "✅ Step submitted: $STEP_ID"
echo "📊 Monitor progress:"
echo "   aws emr describe-step --cluster-id $CLUSTER_ID --step-id $STEP_ID"