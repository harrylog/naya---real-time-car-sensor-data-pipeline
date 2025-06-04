#!/usr/bin/env python3
"""
Simple Kafka Consumer to verify data
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaConsumer") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()

def main():
    KAFKA_SERVERS = "b-1.sparkkafkapipeline.l3k3m3.c22.kafka.us-east-1.amazonaws.com:9092,b-2.sparkkafkapipeline.l3k3m3.c22.kafka.us-east-1.amazonaws.com:9092"
    KAFKA_TOPIC = "sensors-sample"
    
    spark = create_spark_session()
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON and show data
    parsed_df = df.select(
        col("timestamp"),
        col("value").cast("string").alias("json_data")
    )
    
    # Output to console
    query = parsed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    query.awaitTermination()

if __name__ == "__main__":
    main()