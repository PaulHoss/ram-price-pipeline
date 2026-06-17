# Move data into data lakes
import json
import boto3
import os

def bronze_lake_append(payload: dict, run_date: str, bucket: str = None) -> str:
    """
    Appends a single product payload to a daily-partitioned JSONL file
    inside the S3 Bronze data lake layer.

    Returns the S3 key written to for logging purposes.
    """
    # Pull bucket name from environment variable (set via GitHub Secrets)
    if bucket is None:
        bucket = os.environ["AWS_S3_BUCKET"]

    # Define the S3 key (think of this like a file path inside your bucket)
    s3_key = f"raw/{run_date}_scrapes.jsonl"

    # Initialize the S3 client (credentials come automatically from environment)
    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))

    # S3 doesn't support native append, so we read the existing file first (if it exists),
    # add our new line, then write the whole thing back.
    existing_content = ""
    try:
        response = s3.get_object(Bucket=bucket, Key=s3_key)
        existing_content = response["Body"].read().decode("utf-8")
    except s3.exceptions.NoSuchKey:
        pass  # File doesn't exist yet — that's fine, we'll create it
    except Exception as e:
        print(f"Warning: Could not read existing S3 file: {e}")

    # Append the new line
    updated_content = existing_content + json.dumps(payload) + "\n"

    # Write back to S3
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=updated_content.encode("utf-8"),
        ContentType="application/json"
    )

    return f"s3://{bucket}/{s3_key}"