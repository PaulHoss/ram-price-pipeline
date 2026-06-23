"""
Queries the Gold Athena table (fct_ram_prices) and exports results to a CSV
file for use as an Evidence dashboard data source.

Run before building the Evidence dashboard:
    python scripts/export_csv.py

In GitHub Actions, AWS credentials come from environment variables:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET
"""

import boto3
import csv
import io
import os
import time

# Athena config
DATABASE = "ram_price_dbt_gold"
TABLE = "fct_ram_prices"
QUERY = f"SELECT * FROM {DATABASE}.{TABLE} ORDER BY price_date ASC"

# S3 config — reuses existing athena-results/ prefix
S3_BUCKET = os.environ.get("AWS_S3_BUCKET", "ram-price-tracker")
S3_RESULTS_PREFIX = "athena-results/"
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Output path for Evidence CSV source
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "dashboard", "sources", "prices")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "prices.csv")


def run_athena_query():
    """Submits query to Athena and waits for completion. Returns query execution ID."""
    athena = boto3.client("athena", region_name=REGION)

    print(f"Submitting Athena query: {QUERY}")
    response = athena.start_query_execution(
        QueryString=QUERY,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={
            "OutputLocation": f"s3://{S3_BUCKET}/{S3_RESULTS_PREFIX}"
        }
    )
    query_id = response["QueryExecutionId"]
    print(f"Query ID: {query_id}")

    # Poll until complete
    while True:
        status_response = athena.get_query_execution(QueryExecutionId=query_id)
        state = status_response["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            print("Query succeeded.")
            return query_id
        elif state in ["FAILED", "CANCELLED"]:
            reason = status_response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
            raise RuntimeError(f"Athena query {state}: {reason}")
        else:
            print(f"Query state: {state} — waiting...")
            time.sleep(3)


def download_results(query_id):
    """Downloads query result CSV from S3 and returns rows as a list of dicts."""
    s3 = boto3.client("s3", region_name=REGION)
    s3_key = f"{S3_RESULTS_PREFIX}{query_id}.csv"

    print(f"Downloading results from s3://{S3_BUCKET}/{s3_key}")
    response = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
    content = response["Body"].read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    print(f"Downloaded {len(rows)} rows.")
    return rows


def export_csv(rows):
    """Writes rows to the Evidence CSV source file."""
    if not rows:
        print("No rows returned from Athena — CSV not written.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = list(rows[0].keys())
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} rows to {OUTPUT_FILE}")


def main():
    query_id = run_athena_query()
    rows = download_results(query_id)
    export_csv(rows)


if __name__ == "__main__":
    main()
