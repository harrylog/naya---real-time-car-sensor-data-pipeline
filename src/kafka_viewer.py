#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def main():
    spark = SparkSession.builder \
        .appName("TopicViewer") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()
    
    KAFKA_SERVERS = "b-1.sparkkafkapipeline.44yvdh.c22.kafka.us-east-1.amazonaws.com:9092,b-2.sparkkafkapipeline.44yvdh.c22.kafka.us-east-1.amazonaws.com:9092"
    
    # View sensors-sample (your generated data)
    print("=== SENSORS-SAMPLE TOPIC (Raw Sensor Data) ===")
    df1 = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
        .option("subscribe", "sensors-sample") \
        .option("startingOffsets", "earliest") \
        .load()
    
    message_count = df1.count()
    print(f"📊 Total messages: {message_count}")
    
    if message_count > 0:
        print("🔍 Sample raw sensor data:")
        df1.select(col("value").cast("string")).show(5, truncate=False)
    else:
        print("❌ No messages found")
    
    # View samples-enriched (if any processed)
    print("\n=== SAMPLES-ENRICHED TOPIC (Enriched Data) ===")
    try:
        df2 = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
            .option("subscribe", "samples-enriched") \
            .option("startingOffsets", "earliest") \
            .load()
        
        enriched_count = df2.count()
        print(f"📊 Total enriched messages: {enriched_count}")
        
        if enriched_count > 0:
            print("🔍 Sample enriched data:")
            df2.select(col("value").cast("string")).show(3, truncate=False)
        else:
            print("❌ No enriched messages (due to offset error)")
    except Exception as e:
        print(f"Topic may not exist: {e}")
    
    spark.stop()

if __name__ == "__main__":
    main()
