# Spark & Kafka Real-Time Data Pipeline on AWS

Real-time car sensor monitoring system using PySpark, Kafka, and AWS services.

## Overview

Fleet management pipeline that:
- Generates real-time car sensor data (20 cars, 20 events/second)
- Enriches data with car details (brand, model, color)
- Detects driving alerts (speeding, wrong gear, high RPM)
- Provides real-time aggregations and monitoring

## Architecture

```
S3 (Cars) → PySpark → Kafka (sensors) → PySpark → Kafka (enriched) → PySpark → Console (alerts)
```

**Tech Stack**: EMR (PySpark), MSK (Kafka), S3, Terraform

## Complete Setup Guide

### Prerequisites
```bash
# Ensure you have these tools configured
aws configure
terraform --version
```

### Step 1: Deploy Infrastructure
```bash
cd terraform
terraform init
terraform apply -target=module.msk -target=module.emr
```

**Expected output:**
- ✅ EMR cluster ID: `j-XXXXX`
- ✅ MSK connection string: `b-1.sparkkafka...`
- ✅ S3 bucket with dimension data

### Step 2: Update Script Configuration
```bash
# Get the terraform outputs
terraform output msk_connection_info
terraform output emr_cluster_id

# Update these files with the actual values:
# - data_generator.py: KAFKA_SERVERS, CLUSTER_ID
# - data_enrichment.py: KAFKA_SERVERS
# - run_pipeline.sh: CLUSTER_ID
```

### Step 3: Upload Scripts
```bash
# Upload all pipeline scripts to S3
aws s3 cp data_generator.py s3://$(terraform output -raw bucket_name)/scripts/
aws s3 cp data_enrichment.py s3://$(terraform output -raw bucket_name)/scripts/
aws s3 cp kafka_viewer.py s3://$(terraform output -raw bucket_name)/scripts/
```

### Step 4: Run Data Pipeline
```bash
# Start data generator (runs for 2 minutes)
./run_pipeline.sh

# Wait for completion, then run enrichment
aws emr add-steps --cluster-id j-XXXXX --steps '[{
  "Name": "DataEnrichment",
  "ActionOnFailure": "CONTINUE",
  "Jar": "command-runner.jar",
  "Args": ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0", "s3://BUCKET/scripts/data_enrichment.py"]
}]'

# View the actual JSON data in Kafka topics
aws emr add-steps --cluster-id j-XXXXX --steps '[{
  "Name": "TopicViewer",
  "ActionOnFailure": "CONTINUE",
  "Jar": "command-runner.jar",
  "Args": ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0", "s3://BUCKET/scripts/kafka_viewer.py"]
}]'
```

### Step 5: Monitor & Verify Results
```bash
# Check all step statuses
aws emr list-steps --cluster-id j-XXXXX

# View specific step logs
aws emr describe-step --cluster-id j-XXXXX --step-id s-XXXXX

# Or via AWS Console: EMR → Cluster → Steps → Click step → stdout
```

##  Expected Results & Screenshots

### Data Generator Success:
```
 Starting Data Generator...
Loaded 20 cars
Iteration 1: Sent 20 events to sensors-sample
   Sample: Car 8459042 - Speed: 173, RPM: 5878, Gear: 6
```

### Data Enrichment Success:
```
 Starting Data Enrichment...
Loaded dimension tables: Cars: 20, Models: 7, Colors: 7
 Data enrichment streaming started...
```

### Kafka Topic Data (from TopicViewer):
```json
{"event_id":"uuid123","car_id":8459042,"speed":173,"rpm":5878,"gear":6}
{"event_id":"uuid456","car_id":6572047,"speed":85,"rpm":3200,"gear":3}
```

** Screenshots available in `/docs` directory:**
- EMR cluster status and step execution
- Pipeline output logs with data generation
- Kafka topic viewer showing JSON messages
- End-to-end data flow verification

## 🔧 Troubleshooting

| Issue                   | Solution                                                            |
| ----------------------- | ------------------------------------------------------------------- |
| Step won't start        | Check previous step is COMPLETED                                    |
| "Offset changed" errors | Clear checkpoints: `aws s3 rm s3://bucket/checkpoints/ --recursive` |
| No data in TopicViewer  | Verify KAFKA_SERVERS in scripts match terraform output              |
| EMR step fails          | Check IAM permissions and security groups                           |

## Cost Management

**Daily Costs:**
- EMR m5.xlarge: ~$23/day (when running)
- MSK kafka.t3.small: ~$5/day (when running)
- S3 storage: ~$0.01/day
- **Total**: ~$28/day during development

**Cost Optimization:**
```bash
# End of development session - destroy expensive resources
terraform destroy -target=module.emr -target=module.msk

# Keeps S3 data intact for next session
# Saves ~$28/day

# Next session - recreate infrastructure  
terraform apply -target=module.msk -target=module.emr
```

##  Project Structure

```
spark-kafka-pipeline/
├── terraform/
│   ├── modules/
│   │   ├── emr/          # EMR cluster configuration
│   │   └── msk/          # Kafka cluster configuration
│   ├── main.tf           # Main terraform configuration
│   └── outputs.tf        # Infrastructure outputs
├── src/
│   ├── data_generator.py    # Stage 4: Real-time data generation
│   ├── data_enrichment.py   # Stage 5: Data enrichment with joins
│   ├── kafka_viewer.py      # Utility: View Kafka topic data
│   └── run_pipeline.sh      # EMR step submission script
├── docs/
│   └── screenshots/         # Pipeline execution evidence
└── README.md
```

##  Learning Outcomes

**Technical Skills Demonstrated:**
- Infrastructure as Code with Terraform modules
- Real-time data streaming with Apache Kafka
- Big data processing with PySpark Structured Streaming
- AWS cloud services integration (EMR, MSK, S3)
- Data pipeline debugging and monitoring

**Data Engineering Patterns:**
- Lambda architecture (batch + streaming)
- Event-driven data processing
- Dimensional data modeling
- Real-time anomaly detection
- Cost-optimized cloud deployments

---

** Ready for production data engineering roles!**