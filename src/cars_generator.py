# src/cars_generator.py
"""
Cars Generator PySpark Job
Generates 20 cars with random data and saves to S3
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import random
import sys

def generate_cars(spark, output_path):
    """Generate 20 cars with random data"""
    
    # Generate 20 unique car records
    cars_data = []
    used_car_ids = set()
    
    for i in range(20):
        # Generate unique 7-digit car_id
        while True:
            car_id = random.randint(1000000, 9999999)
            if car_id not in used_car_ids:
                used_car_ids.add(car_id)
                break
        
        # Generate other random fields
        driver_id = random.randint(100000000, 999999999)  # 9 digits
        model_id = random.randint(1, 7)  # 1 to 7
        color_id = random.randint(1, 7)  # 1 to 7
        
        cars_data.append((car_id, driver_id, model_id, color_id))
    
    # Create DataFrame
    columns = ["car_id", "driver_id", "model_id", "color_id"]
    cars_df = spark.createDataFrame(cars_data, columns)
    
    # Show sample data
    print("Generated Cars Data:")
    cars_df.show(10)
    print(f"Total cars generated: {cars_df.count()}")
    
    # Save to S3 as CSV with header
    cars_df.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)
    
    print(f"Cars data saved to: {output_path}")

def main():
    # Get S3 output path from command line arguments
    if len(sys.argv) != 2:
        print("Usage: spark-submit cars_generator.py <s3_output_path>")
        print("Example: spark-submit cars_generator.py s3a://your-bucket/data/dims/cars/")
        sys.exit(1)
    
    output_path = sys.argv[1]
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("CarsGenerator") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    print(f"Starting Cars Generation Job...")
    print(f"Output path: {output_path}")
    
    # Generate cars
    generate_cars(spark, output_path)
    
    # Stop Spark session
    spark.stop()
    print("Cars generation completed successfully!")

if __name__ == "__main__":
    main()
