#!/usr/bin/env python3
"""
Data Generator - Stage 4 of Spark & Kafka Pipeline
Reads cars from S3 and generates continuous sensor data to Kafka
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
import time
import random
import uuid
from datetime import datetime

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("DataGenerator") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()

def read_cars_from_s3(spark, s3_path):
    """Read the 20 cars from S3"""
    print(f"Reading cars from: {s3_path}")
    
    cars_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(s3_path)
    
    cars_list = cars_df.collect()
    print(f"Loaded {len(cars_list)} cars")
    
    # Print first few cars for verification
    for i, car in enumerate(cars_list[:3]):
        print(f"Car {i+1}: ID={car.car_id}, Driver={car.driver_id}, Model={car.model_id}, Color={car.color_id}")
    
    return cars_list

def generate_sensor_event(car):
    """Generate a single sensor event for a car"""
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": datetime.now().isoformat(),
        "car_id": car.car_id,
        "speed": random.randint(0, 200),
        "rpm": random.randint(0, 8000),
        "gear": random.randint(1, 7)
    }

def send_to_kafka(spark, events, kafka_servers, topic):
    """Send events to Kafka topic"""
    
    # Convert events to JSON strings
    events_json = [json.dumps(event) for event in events]
    
    # Create DataFrame
    events_df = spark.createDataFrame(
        [(json_str,) for json_str in events_json],
        ["value"]
    )
    
    # Write to Kafka
    events_df.write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("topic", topic) \
        .save()

def main():
    # Configuration - UPDATE THESE VALUES
    S3_CARS_PATH = "s3a://spark-kafka-pipeline-zn1fp2wf/data/dims/cars/"
    KAFKA_SERVERS = "REPLACE_WITH_MSK_BOOTSTRAP_SERVERS"  # Will get from terraform output
    KAFKA_TOPIC = "sensors-sample"
    
    print("🚗 Starting Data Generator...")
    print(f"S3 Path: {S3_CARS_PATH}")
    print(f"Kafka Topic: {KAFKA_TOPIC}")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read cars from S3 (one-time read)
        cars = read_cars_from_s3(spark, S3_CARS_PATH)
        
        print(f"\n🔄 Starting continuous data generation...")
        print(f"Generating sensor data for {len(cars)} cars every second")
        print("Press Ctrl+C to stop\n")
        
        iteration = 0
        while True:
            iteration += 1
            
            # Generate events for all cars
            events = []
            for car in cars:
                event = generate_sensor_event(car)
                events.append(event)
            
            # Send to Kafka
            try:
                send_to_kafka(spark, events, KAFKA_SERVERS, KAFKA_TOPIC)
                print(f"📤 Iteration {iteration}: Sent {len(events)} events to {KAFKA_TOPIC}")
                
                # Show sample event
                if iteration % 10 == 1:  # Show every 10th iteration
                    sample_event = events[0]
                    print(f"   Sample: Car {sample_event['car_id']} - Speed: {sample_event['speed']}, RPM: {sample_event['rpm']}, Gear: {sample_event['gear']}")
                
            except Exception as e:
                print(f"❌ Error sending to Kafka: {e}")
                time.sleep(5)  # Wait before retrying
                continue
            
            # Wait 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping data generator...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        spark.stop()
        print("✅ Data generator stopped")

if __name__ == "__main__":
    main()
