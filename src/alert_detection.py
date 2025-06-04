#!/usr/bin/env python3
"""
Alert Detection - Stage 6 of Spark & Kafka Pipeline
Filters enriched data to detect alerts and send to alert-data topic
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("AlertDetection") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()

def detect_alerts(enriched_df):
    """Filter data to detect alert conditions"""
    
    # Parse JSON from Kafka
    enriched_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("car_id", IntegerType(), True),
        StructField("speed", IntegerType(), True),
        StructField("rpm", IntegerType(), True),
        StructField("gear", IntegerType(), True),
        StructField("expected_gear", IntegerType(), True),
        StructField("driver_id", IntegerType(), True),
        StructField("brand_name", StringType(), True),
        StructField("model_name", StringType(), True),
        StructField("color_name", StringType(), True)
    ])
    
    parsed_df = enriched_df.select(
        from_json(col("value").cast("string"), enriched_schema).alias("data")
    ).select("data.*")
    
    # Alert conditions:
    # - Speed is greater than 120
    # - Expected gear is not equal to actual gear  
    # - RPM is greater than 6000
    alert_df = parsed_df.filter(
        (col("speed") > 120) | 
        (col("expected_gear") != col("gear")) | 
        (col("rpm") > 6000)
    )
    
    return alert_df

def main():
    # Configuration
    KAFKA_SERVERS = "b-1.sparkkafkapipeline.5jgeuh.c22.kafka.us-east-1.amazonaws.com:9092,b-2.sparkkafkapipeline.5jgeuh.c22.kafka.us-east-1.amazonaws.com:9092"
    INPUT_TOPIC = "samples-enriched"
    OUTPUT_TOPIC = "alert-data"
    S3_BUCKET = "spark-kafka-pipeline-zn1fp2wf"
    
    print("🚨 Starting Alert Detection...")
    print(f"Input Topic: {INPUT_TOPIC}")
    print(f"Output Topic: {OUTPUT_TOPIC}")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read from enriched Kafka topic
        enriched_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
            .option("subscribe", INPUT_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Detect alerts
        alerts_df = detect_alerts(enriched_df)
        
        # Convert back to JSON for Kafka output
        output_df = alerts_df.select(
            to_json(struct("*")).alias("value")
        )
        
        # Write to alert Kafka topic
        query = output_df \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
            .option("topic", OUTPUT_TOPIC) \
            .option("checkpointLocation", f"s3a://{S3_BUCKET}/checkpoints/alerts/") \
            .outputMode("append") \
            .start()
        
        print("🚨 Alert detection streaming started...")
        print("Monitoring for:")
        print("  - Speed > 120")
        print("  - Expected gear != actual gear")  
        print("  - RPM > 6000")
        print("Press Ctrl+C to stop")
        
        query.awaitTermination()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        spark.stop()
        print("✅ Alert detection stopped")

if __name__ == "__main__":
    main()