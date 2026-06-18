# One-time setup script: creates a Glue database and table so Athena can query
# the Bronze S3 data lake. Run this once via GitHub Actions (see setup_athena.yml).
# Safe to re-run — it checks for existing resources before creating them.

import boto3
import os

def setup_athena():
    region = os.environ.get("AWS_REGION", "us-east-1")
    bucket = os.environ["AWS_S3_BUCKET"]

    glue = boto3.client("glue", region_name=region)
    athena = boto3.client("athena", region_name=region)

    DB_NAME = "ram_price_tracker"
    TABLE_NAME = "bronze_scrapes"
    S3_DATA_PATH = f"s3://{bucket}/raw/"
    S3_RESULTS_PATH = f"s3://{bucket}/athena-results/"

    
    # Create Glue database - Think of this like a schema in SQL — just a named container for tables.
    print(f"Creating Glue database: {DB_NAME}")
    try:
        glue.create_database(
            DatabaseInput={
                "Name": DB_NAME,
                "Description": "Bronze data lake for RAM price tracker project"
            }
        )
        print(f"  -> Database '{DB_NAME}' created.")
    except glue.exceptions.AlreadyExistsException:
        print(f"  -> Database '{DB_NAME}' already exists. Skipping.")

    # Create Glue table - This is the metadata definition that tells Athena:
    #   Where the data lives (S3 path)
    #   What format it's in (JSON lines)
    #   What the columns are and their types
    #
    # IMPORTANT: The S3 path points to the folder, not a specific file.
    # Athena will automatically read ALL .jsonl files under raw/ — including
    # every daily file your scraper has written and will write in the future.
    print(f"Creating Glue table: {TABLE_NAME}")

    # Column definitions must match exactly what your scraper writes to S3.
    # Types use Hive/Athena type syntax (string, double, boolean, timestamp).
    columns = [
        {"Name": "mpn",            "Type": "string",  "Comment": "Manufacturer part number"},
        {"Name": "brand",          "Type": "string",  "Comment": "e.g. Corsair, G.SKILL"},
        {"Name": "gen",            "Type": "string",  "Comment": "DDR4 or DDR5"},
        {"Name": "model",          "Type": "string",  "Comment": "e.g. Vengeance, Ripjaws S5"},
        {"Name": "scraped_title",  "Type": "string",  "Comment": "Raw product title from retailer"},
        {"Name": "currency",       "Type": "string",  "Comment": "e.g. USD"},
        {"Name": "price",          "Type": "double",  "Comment": "Scraped price as decimal"},
        {"Name": "availability",   "Type": "string",  "Comment": "e.g. InStock, OutOfStock"},
        {"Name": "condition",      "Type": "string",  "Comment": "e.g. NewCondition"},
        {"Name": "seller",         "Type": "string",  "Comment": "Seller name on the marketplace"},
        {"Name": "marketplace",    "Type": "string",  "Comment": "e.g. Newegg, Best Buy"},
        {"Name": "date",           "Type": "string",  "Comment": "Scrape date YYYY-MM-DD"},
        {"Name": "timestamp",      "Type": "string",  "Comment": "Full ISO 8601 UTC timestamp"},
        {"Name": "pipeline_status","Type": "string",  "Comment": "Pass or Fail"},
        {"Name": "url_fetch_method","Type": "string", "Comment": "e.g. STANDARD_REQUESTS, CURL_CFFI"},
        {"Name": "fetch_error",    "Type": "string",  "Comment": "Fetch error message or null"},
        {"Name": "parse_error",    "Type": "string",  "Comment": "Parse error message or null"},
    ]

    try:
        glue.create_table(
            DatabaseName=DB_NAME,
            TableInput={
                "Name": TABLE_NAME,
                "Description": "Daily raw price scrapes — Bronze layer",
                "StorageDescriptor": {
                    "Columns": columns,
                    "Location": S3_DATA_PATH,
                    # TextInputFormat + JsonSerDe is the standard combo for JSONL files
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        # JsonSerDe maps each JSON field name to the column by name,
                        # so column order here doesn't matter — it matches by key.
                        "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                        "Parameters": {
                            # Tells Athena to return NULL instead of crashing when
                            # a JSON field is missing from a row (e.g. fetch_error)
                            "ignore.malformed.json": "true"
                        }
                    },
                    "Compressed": False,
                },
                # No partition keys for now — keeps setup simple. Every query
                # will scan all files under raw/, which is fine at this data volume.
                # (We can add date partitioning in a future iteration if needed.)
                "PartitionKeys": [],
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    # Tells Athena this is an external table — data lives in S3
                    # and should NOT be deleted if the table is dropped in Glue.
                    "EXTERNAL": "TRUE",
                }
            }
        )
        print(f"  -> Table '{TABLE_NAME}' created.")
    except glue.exceptions.AlreadyExistsException:
        print(f"  -> Table '{TABLE_NAME}' already exists. Skipping.")

    # Create the Athena query results folder in S3
    # Athena requires a dedicated S3 location to write query results to.
    # We create a zero-byte placeholder object to ensure the prefix exists.
    print(f"Ensuring Athena results path exists: {S3_RESULTS_PATH}")
    s3 = boto3.client("s3", region_name=region)
    s3.put_object(Bucket=bucket, Key="athena-results/.keep", Body=b"")
    print(f"  -> Results path ready.")

    # Verify setup by running a test query via the Athena API
    # This is a DDL query (free — not charged by AWS) that just confirms
    # Athena can see the table and read its schema.
    print("Running verification query in Athena...")
    response = athena.start_query_execution(
        QueryString=f"SHOW COLUMNS IN {DB_NAME}.{TABLE_NAME}",
        QueryExecutionContext={"Database": DB_NAME},
        ResultConfiguration={"OutputLocation": S3_RESULTS_PATH}
    )
    query_id = response["QueryExecutionId"]
    print(f"  -> Query submitted. Execution ID: {query_id}")
    print(f"  -> Check results in AWS Athena console or at: {S3_RESULTS_PATH}")
    print()
    print("=" * 60)
    print("Setup complete! You can now query your data in Athena with:")
    print(f"  SELECT * FROM {DB_NAME}.{TABLE_NAME} LIMIT 10;")
    print("=" * 60)

if __name__ == "__main__":
    setup_athena()
