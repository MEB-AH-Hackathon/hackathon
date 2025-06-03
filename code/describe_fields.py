import json
import pandas as pd
from collections import defaultdict
import os

# Load the JSON file
input_path = os.path.join("..", "json_data", "vaers_subset.json")
with open(input_path, "r") as f:
    data = json.load(f)

# Normalize into a DataFrame
df = pd.json_normalize(data)

# Helper to extract unique values from lists and scalars
def get_unique_values(series):
    all_values = set()
    for item in series.dropna():
        if isinstance(item, list):
            all_values.update(item)
        else:
            all_values.add(item)
    return all_values

# Collect fields with <= 4 unique values
few_unique_values = {}

for column in df.columns:
    unique_vals = get_unique_values(df[column])
    if len(unique_vals) <= 4:
        # Convert any non-serializable types to string
        few_unique_values[column] = list(map(str, unique_vals))

# Output to JSON file
output_path = os.path.join("..", "json_data", "few_unique_fields.json")
with open(output_path, "w") as f:
    json.dump(few_unique_values, f, indent=2)

print(f"Wrote summary to {output_path}")
