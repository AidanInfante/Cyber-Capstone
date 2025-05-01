import pandas as pd
import json
from pandas import json_normalize
import os

input_file = "ember_features.csv"
output_file = "cleaned_features.csv"

# This is a list of columns in the CSV that need to be flattened
json_columns = ['general', 'header', 'section', 'imports', 'exports', 'datadirectories']

# This controls how many rows to process at once to help with memory usage
chunk_size = 500

# This tracks whether this is the first chunk to make sure headers are only written once
first_chunk = True

# Making sure the directory for the output file exists
output_dir = os.path.dirname(output_file)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)


# This processes the input CSV file in chunks to avoid memory overload
for i, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size)):
    print(f"\nProcessing chunk {i+1}...")

    # Drops non-feature columns to focus on raw features
    base = chunk.drop(columns=['sha256', 'md5', 'appeared', 'avclass'], errors='ignore')

    # Loop to go through each column and expand it into multiple flat columns
    for col in json_columns:
        print(f"   ➤ Flattening column: {col}")
        if col not in base.columns:
            continue  # Skip if column is missing

        # Converts JSON string to a Python object safely
        def safe_load(val):
            try:
                return json.loads(val)
            except Exception:
                return None  # Returns None if it can't be parsed

        # Apply the JSON parser to the column
        base[col] = base[col].apply(safe_load)

        # Check for valid JSON entries
        valid = base[col].notnull()
        if valid.any():
            # If the JSON object is a list, this converts to DataFrame directly
            if isinstance(base[col][valid].iloc[0], list):
                expanded = pd.DataFrame(base[col][valid].tolist()).add_prefix(f"{col}_")
            else:
                # If it's a dictionary or nested object, flatten it using json_normalize
                expanded = json_normalize(base[col][valid])
                expanded.columns = [f"{col}_{subcol}" for subcol in expanded.columns]

            # Keep alignment of indexes to merge flattened features back
            expanded.index = base[valid].index

            # Drop original JSON column and add flattened columns
            base = base.drop(columns=[col])
            base = pd.concat([base, expanded], axis=1)
        else:
            # If there is no valid JSON data, just drop the column
            base = base.drop(columns=[col])

    # Fill any missing values with 0s
    base = base.fillna(0)

    # Write the processed chunk to the output CSV
    base.to_csv(output_file, index=False, mode='w' if first_chunk else 'a', header=first_chunk)

    # After first chunk, don't write headers again
    first_chunk = False
    print(f"Finished chunk {i+1} with {len(base)} rows")

print("\nAll chunks have been processed. Flattened data saved to cleaned_features.csv")
