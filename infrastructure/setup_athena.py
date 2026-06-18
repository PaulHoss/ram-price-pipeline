"""
Infrastructure-as-Code (IaC) initialization script to provision 
AWS Glue Data Catalog resources and map AWS Athena schemas over the Bronze S3 Data Lake.
"""

import os
import boto3


def setup_athena():
    """
    Provisions the AWS Glue database and external table schemas required 
    to enable serverless SQL queries via Amazon Athena over raw S3 JSON Lines data.
    """
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    # Fail-fast constraint validation for required deployment infrastructure targets
    if "AWS_S3_BUCKET" not in os.environ:
        raise KeyError("Environment variable 'AWS_S3_BUCKET' must be set prior to execution.")
        
    bucket = os.environ["AWS_S3_BUCKET"]

    # Initialize AWS SDK service clients
    glue = boto3.client("glue", region_name=region)
    athena = boto3.client("athena", region_name=region)

    DB_NAME = "ram_price_tracker"
    TABLE_NAME = "bronze_scrapes"
    S3_DATA_PATH = f"s3://{bucket}/raw/"
    S3_RESULTS_PATH = f"s3://{bucket}/athena-results/"

    # -------------------------------------------------------------------------
    # 1. AWS Glue Database Provisioning
    # -------------------------------------------------------------------------
    print(f"Initializing Glue Database: {DB_NAME}")
    try:
        glue.create_database(
            DatabaseInput={
                "Name": DB_NAME,
                "Description": "Bronze zone data catalog container for the hardware intelligence pipeline."
            }
        )
        print(f"  -> Database '{DB_NAME}' provisioned successfully.")
    except glue.exceptions.AlreadyExistsException:
        print(f"  -> Database '{DB_NAME}' already exists. Idempotent skip applied.")

    # -------------------------------------------------------------------------
    # 2. AWS Glue External Table Schema Definition
    # -------------------------------------------------------------------------
    print(f"Registering External Schema Matrix: {DB_NAME}.{TABLE_NAME}")
    
    # Construct schema schema definition to parse unstructured JSON Lines records
    table_input = {
        "Name": TABLE_NAME,
        "Description": "External table mapping over S3 append-only raw JSONL scrapers dataset.",
        "CreateTime": 0,
        "Retention": 0,
        "StorageDescriptor": {
            "Columns": [
                {"Name": "mpn", "Type": "string"},
                {"Name": "brand", "Type": "string"},
                {"Name": "gen", "Type": "string"},
                {"Name": "model", "Type": "string"},
                {"Name": "scraped_title", "Type": "string"},
                {"Name": "currency", "Type": "string"},
                {"Name": "price", "Type": "double"},
                {"Name": "availability", "Type": "string"},
                {"Name": "condition", "Type": "string"},
                {"Name": "seller", "Type": "string"},
                {"Name": "marketplace", "Type": "string"},
                {"Name": "date", "Type": "string"},
                {"Name": "timestamp", "Type": "string"},
                {"Name": "pipeline_status", "Type": "string"},
                {"Name": "url_fetch_method", "Type": "string"},
                {"Name": "fetch_error", "Type": "string"},
                {"Name": "parse_error", "Type": "string"}
            ],
            "Location": S3_DATA_PATH,
            "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            "Compressed": False,
            "NumberOfBuckets": -1,
            "SerdeInfo": {
                "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                "Parameters": {
                    "paths": "availability,brand,condition,currency,date,fetch_error,gen,marketplace,model,mpn,parse_error,pipeline_status,price,scraped_title,seller,timestamp,url_fetch_method"
                }
            },
            "StoredAsSubDirectories": False
        },
        "TableType": "EXTERNAL_TABLE",
        "Parameters": {
            "classification": "json",
            "typeOfData": "file"
        }
    }

    try:
        glue.create_table(DatabaseName=DB_NAME, TableInput=table_input)
        print(f"  -> External table '{TABLE_NAME}' registered successfully.")
    except glue.exceptions.AlreadyExistsException:
        # Re-register table configurations to safely catch upstream operational schema modifications
        print(f"  -> Table '{TABLE_NAME}' already exists. Overwriting definition to apply upstream schema updates...")
        glue.update_table(DatabaseName=DB_NAME, TableName=TABLE_NAME, TableInput=table_input)
        print(f"  -> External table '{TABLE_NAME}' configuration updated.")

    # -------------------------------------------------------------------------
    # 3. Amazon Athena Direct Query Storage Prerequisites
    # -------------------------------------------------------------------------
    print(f"Validating Athena Workgroup Execution Target S3 Location: {S3_RESULTS_PATH}")
    s3 = boto3.client("s3", region_name=region)
    
    # Establish a zero-byte operational placeholder to verify target directory accessibility
    s3.put_object(Bucket=bucket, Key="athena-results/.keep", Body=b"")
    print("  -> Query execution workspace placeholder confirmed.")

    # -------------------------------------------------------------------------
    # 4. End-to-End Pipeline Lineage Verification
    # -------------------------------------------------------------------------
    print("Submitting integration verification compilation query to Athena API...")
    try:
        response = athena.start_query_execution(
            QueryString=f"SHOW COLUMNS IN {DB_NAME}.{TABLE_NAME}",
            QueryExecutionContext={"Database": DB_NAME},
            ResultConfiguration={"OutputLocation": S3_RESULTS_PATH}
        )
        query_id = response["QueryExecutionId"]
        print(f"  -> Verification pipeline query submitted successfully. Task Execution ID: {query_id}")
        print(f"  -> Output lineage tracking active at destination path: {S3_RESULTS_PATH}")
    except Exception as e:
        print(f"  -> WARNING: Athena execution validation skipped or failed: {str(e)}")
        
    print("\n" + "=" * 60)
    print("Infrastructure Configuration Complete. Ingestion analytics catalog exposed.")
    print(f"  Target Warehouse Syntax: SELECT * FROM {DB_NAME}.{TABLE_NAME} LIMIT 10;")
    print("=" * 60)


if __name__ == "__main__":
    setup_athena()