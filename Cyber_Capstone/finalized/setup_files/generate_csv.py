import json
import pandas as pd
import glob
import os

# Defines the path to my EMBER directory
ember_path = "/ember-dataset"

# Finds all train_features_*.jsonl files in the directory
jsonl_files = glob.glob(os.path.join(ember_path, "train_features_*.jsonl"))

print(f"Found {len(jsonl_files)} .jsonl files...")

all_rows = []

for file in jsonl_files:
    print(f"Reading: {file}")
    with open(file, 'r') as f:
        for line in f:
            data = json.loads(line)
            all_rows.append(data)

# Convert to a DataFrame
df = pd.DataFrame(all_rows)

# Save to file
output_csv = os.path.join(ember_path, "ember_features.csv")
df.to_csv(output_csv, index=False)
print(f"\nDone! Saved to {output_csv}")
