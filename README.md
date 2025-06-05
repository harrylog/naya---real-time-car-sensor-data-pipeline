# Spark & Kafka Real-Time Data Pipeline on AWS

Real-time car sensor monitoring system using PySpark, Kafka, and AWS services.

## 🎯 Overview

Fleet management pipeline that:
- Generates real-time car sensor data
- Enriches data with car details (brand, model, color)
- Detects driving alerts (speeding, wrong gear, high RPM)
- Provides real-time aggregations

## 🏗️ Architecture

```
S3 (Cars) → PySpark → Kafka (sensors) → PySpark → Kafka (enriched) → PySpark → Console (alerts)
```

**Stack**: EMR (PySpark), MSK (Kafka), S3, Terraform


terraform apply -target=module.msk -target=module.emr

./run_pipeline.sh                    # Data generator (2 min)
aws emr add-steps ... DataEnrichment # After generator completes
aws emr add-steps ... TopicViewer     # View JSON data


aws emr list-steps --cluster-id j-XXXXX
# EMR Console → Steps → Click step → stdout



