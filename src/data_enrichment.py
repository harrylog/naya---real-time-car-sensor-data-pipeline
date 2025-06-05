#!/usr/bin/env python3
"""
Data Enrichment - Stage 5 of Spark & Kafka Pipeline
Enriches sensor data with car details from S3 dimensions
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("DataEnrichment") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()

def load_dimension_tables(spark, bucket_name):
    """Load dimension tables from S3"""
    
    # Load cars
    cars_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(f"s3a://{bucket_name}/data/dims/cars/")
    
    # Load car models
    models_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(f"s3a://{bucket_name}/data/dims/car_models/")
    
    # Load car colors
    colors_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(f"s3a://{bucket_name}/data/dims/car_colors/")
    
    print("Loaded dimension tables:")
    print(f"Cars: {cars_df.count()}")
    print(f"Models: {models_df.count()}")
    print(f"Colors: {colors_df.count()}")
    
    return cars_df, models_df, colors_df

def enrich_sensor_data(sensors_df, cars_df, models_df, colors_df):
    """Enrich sensor data with dimension information"""
    
    # Parse JSON from Kafka
    sensor_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("car_id", IntegerType(), True),
        StructField("speed", IntegerType(), True),
        StructField("rpm", IntegerType(), True),
        StructField("gear", IntegerType(), True)
    ])
    
    parsed_df = sensors_df.select(
        from_json(col("value").cast("string"), sensor_schema).alias("data")
    ).select("data.*")
    
    # Add expected_gear calculation
    enriched_df = parsed_df.withColumn("expected_gear", round(col("speed") / 30))
    
    # Join with cars dimension
    enriched_df = enriched_df.join(cars_df, "car_id", "inner")
    
    # Join with models dimension
    enriched_df = enriched_df.join(models_df, "model_id", "inner")
    
    # Join with colors dimension
    enriched_df = enriched_df.join(colors_df, "color_id", "inner")
    
    # Select and rename columns for final output
    final_df = enriched_df.select(
        col("event_id"),
        col("event_time"),
        col("car_id"),
        col("speed"),
        col("rpm"),
        col("gear"),
        col("expected_gear"),
        col("driver_id"),
        col("car_brand").alias("brand_name"),
        col("car_model").alias("model_name"),
        col("color_name")
    )
    
    return final_df

def main():
    # Configuration
    KAFKA_SERVERS = "b-1.sparkkafkapipeline.44yvdh.c22.kafka.us-east-1.amazonaws.com:9092,b-2.sparkkafkapipeline.44yvdh.c22.kafka.us-east-1.amazonaws.com:9092"
    INPUT_TOPIC = "sensors-sample"
    OUTPUT_TOPIC = "samples-enriched"
    S3_BUCKET = "spark-kafka-pipeline-zn1fp2wf"
    
    print("🔧 Starting Data Enrichment...")
    print(f"Input Topic: {INPUT_TOPIC}")
    print(f"Output Topic: {OUTPUT_TOPIC}")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Load dimension tables (static data)
        cars_df, models_df, colors_df = load_dimension_tables(spark, S3_BUCKET)
        
        # Read from input Kafka topic
        sensors_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
            .option("subscribe", INPUT_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Enrich the data
        enriched_df = enrich_sensor_data(sensors_df, cars_df, models_df, colors_df)
        
        # Convert back to JSON for Kafka output
        output_df = enriched_df.select(
            to_json(struct("*")).alias("value")
        )
        
        # Write to output Kafka topic
        query = output_df \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
            .option("topic", OUTPUT_TOPIC) \
            .option("checkpointLocation", f"s3a://{S3_BUCKET}/checkpoints/enrichment/") \
            .outputMode("append") \
            .start()
        
        print("📊 Data enrichment streaming started...")
        print("Press Ctrl+C to stop")
        
        query.awaitTermination()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        spark.stop()
        print("✅ Data enrichment stopped")

if __name__ == "__main__":
    main()