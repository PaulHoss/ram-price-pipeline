# Move data into data lakes
import os
import json

def bronze_lake_append(payload: dict, run_date: str, base_dir: str = "data") -> str:
    """
    Appends a single product payload to a daily-partitioned JSONL file 
    inside the local immutable Bronze data lake layer.
    
    Returns the full path of the file written to for logging purposes.
    """
    # Define the directory and filename dynamically based on the run date
    dir_path = os.path.join(base_dir, "raw")
    file_name = f"{run_date}_scrapes.jsonl"
    full_path = os.path.join(dir_path, file_name)
    
    # Ensure the local folder structure exists safely
    os.makedirs(dir_path, exist_ok=True)
    
    # Open the file in append mode ('a') and write the payload as a single line
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
        
    return full_path