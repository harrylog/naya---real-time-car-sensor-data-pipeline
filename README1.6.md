# Spark & Kafka Real-Time Data Pipeline on AWS

A comprehensive data engineering project implementing a real-time car sensor monitoring system using PySpark, Kafka, and AWS services, deployed with Infrastructure as Code (Terraform).

## 🎯 Project Overview

This project simulates a **real-time car monitoring system** that:
- Generates synthetic car data and sensor readings
- Streams data through Kafka topics
- Processes data with PySpark Structured Streaming
- Detects driving anomalies and alerts
- Provides real-time aggregations and monitoring

**Use Case**: Fleet management system that monitors vehicle performance, detects dangerous driving patterns (speeding, wrong gear usage, high RPM), and provides real-time analytics.

## 🏗️ Architecture

```
Data Flow:
S3 (Dimensions) → PySpark (Cars Generator) → Kafka → PySpark (Enrichment) → Kafka → PySpark (Alerts) → Console
```

**Tech Stack:**
- **Compute**: Amazon EMR (PySpark)
- **Streaming**: Amazon MSK (Kafka)
- **Storage**: Amazon S3
- **Infrastructure**: Terraform
- **Language**: Python (PySpark)

## 📊 Data Model

### Dimension Tables
- **Car Models**: Brand and model information (Mazda 3, Toyota Corolla, etc.)
- **Car Colors**: Color mappings (Black, Red, White, etc.)
- **Cars**: Generated fleet of 20 vehicles with unique IDs

### Streaming Data
- **Sensor Events**: Real-time car telemetry (speed, RPM, gear, timestamp)
- **Enriched Events**: Sensor data + car details (brand, model, color)
- **Alert Events**: Filtered events for dangerous driving patterns

## 🚀 Project Stages

### ✅ Stage 1: Setup & Foundation (Completed)
**Duration**: Day 1  
**Objective**: Establish AWS infrastructure and dimension data

**What was built:**
- **S3 Bucket**: `spark-kafka-pipeline-zn1fp2wf`
- **Dimension Data**: Car models and colors uploaded as CSV files
- **Terraform Structure**: Base configuration with proper folder organization

**Key Files Created:**
```
terraform/
├── main.tf              # Provider and module configuration
├── variables.tf         # Project variables
├── outputs.tf          # S3 paths and bucket info
└── s3.tf               # S3 bucket and dimension data
```

**Technical Details:**
- S3 bucket with versioning and encryption enabled
- CSV files with car models (7 models) and colors (7 colors)
- Proper folder structure: `/data/dims/car_models/`, `/data/dims/car_colors/`

**Verification Commands:**
```bash
aws s3 ls s3://spark-kafka-pipeline-zn1fp2wf/data/dims/ --recursive
terraform output
```

**Results:**
- ✅ Car models CSV: 7 records (Mazda 3, Toyota Corolla, etc.)
- ✅ Car colors CSV: 7 records (Black, Red, White, etc.)
- ✅ S3 bucket ready for data processing

---

### ✅ Stage 2: EMR & Data Generation (Completed)
**Duration**: Day 1  
**Objective**: Set up Spark processing and generate car fleet data

**What was built:**
- **EMR Cluster**: Single-node Spark cluster via Terraform module
- **IAM Roles**: Service and instance roles with proper permissions
- **PySpark Application**: Cars generator script
- **Data Pipeline**: First ETL job execution

**Infrastructure Created:**
```
terraform/modules/emr/
├── main.tf              # EMR cluster configuration
├── iam.tf              # IAM roles and policies
├── variables.tf        # EMR-specific variables
└── outputs.tf          # Cluster details
```

**Technical Challenges Solved:**
1. **VPC/Subnet Issues**: Created default VPC for clean network setup
2. **Security Groups**: Resolved EMR master/slave security group requirements
3. **IAM Permissions**: Overcame restrictive EMR service policies with admin access
4. **Instance Types**: Found compatible instance type (`m5.xlarge`)

**PySpark Job Details:**
- **Script**: `cars_generator.py`
- **Function**: Generate 20 unique cars with random attributes
- **Output**: CSV file with car_id, driver_id, model_id, color_id
- **Execution**: EMR Step via AWS CLI

**EMR Configuration:**
- **Release**: emr-6.15.0
- **Applications**: Spark only
- **Instance**: m5.xlarge (single node)
- **Auto-termination**: Disabled (manual control for cost management)

**Job Execution Results:**
```bash
# Step Status: COMPLETED
# Generated: 20 cars with unique 7-digit car_ids
# Sample output:
car_id,driver_id,model_id,color_id
8459042,633142716,2,4
6572047,456625863,2,6
...
```

**Cost Management Strategy:**
```bash
# End of day: Destroy cluster
terraform destroy -target=module.emr

# Next day: Recreate cluster  
terraform apply -target=module.emr
```

**Key Learnings:**
- EMR cluster IDs change with each recreation
- Terraform modules enable targeted resource management
- Full admin IAM policies work for development environments
- EMR requires both master and slave security groups

---

### 🔄 Stage 3: MSK (Kafka) Setup (Planned)
**Duration**: Day 2  
**Objective**: Set up managed Kafka for real-time streaming

**Planned Components:**
- Amazon MSK cluster via Terraform
- Kafka topics: `sensors-sample`, `samples-enriched`, `alert-data`
- Network security configuration
- Topic creation and management

---

### 🔄 Stage 4: Real-Time Data Generation (Planned)
**Duration**: Day 3  
**Objective**: Implement streaming data producer

**Planned Components:**
- PySpark Streaming job reading cars from S3
- Generate sensor data every second per car
- Publish to Kafka `sensors-sample` topic
- JSON message format with timestamps

---

### 🔄 Stage 5: Data Enrichment Pipeline (Planned)
**Duration**: Day 4  
**Objective**: Enrich streaming data with dimension tables

**Planned Components:**
- PySpark Structured Streaming consumer
- Join sensor data with car models and colors
- Calculate expected gear based on speed
- Publish enriched data to `samples-enriched` topic

---

### 🔄 Stage 6: Alert Detection System (Planned)
**Duration**: Day 5  
**Objective**: Implement real-time anomaly detection

**Planned Components:**
- Real-time filtering for dangerous driving patterns
- Alert conditions: speed > 120, RPM > 6000, wrong gear
- Publish alerts to `alert-data` topic
- Console output with aggregated metrics

---

### 🔄 Stage 7: Monitoring & Visualization (Planned)
**Duration**: Day 6  
**Objective**: Real-time monitoring and final integration

**Planned Components:**
- 15-minute windowed aggregations
- Color-based statistics
- Maximum speed/RPM tracking
- End-to-end pipeline testing

## 🛠️ Technology Decisions

### Why Amazon EMR?
- Managed Spark service reduces operational overhead
- Auto-scaling capabilities for production workloads
- Integration with S3 and other AWS services
- Support for multiple Spark applications

### Why Amazon MSK?
- Fully managed Kafka reduces infrastructure complexity
- Built-in monitoring and security features
- Seamless AWS integration
- Auto-scaling and multi-AZ deployment

### Why Terraform?
- Infrastructure as Code enables reproducible deployments
- Modular approach allows selective resource management
- Version control for infrastructure changes
- Cost optimization through destroy/recreate workflows

## 📋 Requirements

- **AWS CLI** configured with appropriate permissions
- **Terraform** >= 1.0
- **Python** 3.8+ (for local development)
- **Git** for version control

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd spark-kafka-pipeline

# Deploy S3 infrastructure
cd terraform
terraform init
terraform apply

# Deploy EMR cluster (when needed)
terraform apply -target=module.emr

# Verify deployment
terraform output
aws s3 ls s3://$(terraform output -raw bucket_name)/data/dims/ --recursive
```

## 💰 Cost Management

**Daily Costs (Estimated):**
- S3 Storage: ~$0.01/day
- EMR m5.xlarge: ~$23/day when running
- MSK (planned): ~$11/day when running

**Cost Optimization:**
- Use targeted Terraform apply/destroy for expensive resources
- Single-node EMR cluster for development
- Automated cleanup scripts

**Destroy expensive resources:**
```bash
terraform destroy -target=module.emr
terraform destroy -target=module.msk  # When implemented
```

## 📈 Project Metrics

**Current Status:**
- ✅ Infrastructure modules: 2/7 complete
- ✅ Data generation: Working
- ✅ S3 integration: Working
- 🔄 Streaming pipeline: 0/4 components

**Next Milestone**: MSK setup and first streaming job

## 🤝 Submission Format

This project is designed for academic evaluation with multiple viewing options:

1. **Documentation Review**: Complete codebase and architecture documentation
2. **Live Demonstration**: ReadOnly AWS access for real-time evaluation
3. **Results Package**: Sample outputs and execution screenshots

---

*Last Updated: Day 1 - EMR Stage Complete*
