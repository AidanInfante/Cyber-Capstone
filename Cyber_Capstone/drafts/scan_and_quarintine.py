import os
import shutil
import hashlib
import pandas as pd
import joblib
import ast
import numpy as np
from datetime import datetime

# Configuration
INPUT_CSV = "cleaned_features.csv"
MODEL_PATH = "Infante_Antivirus_Model.joblib"
QUARANTINE_DIR = "quarantine"
OUTPUT_CSV = "predictions_output.csv"

# Ensure quarantine folder exists
os.makedirs(QUARANTINE_DIR, exist_ok=True)

print("Loading Infante Antivirus")
model = joblib.load(MODEL_PATH)

print("Loading cleaned_features.csv")
df = pd.read_csv(INPUT_CSV, on_bad_lines='skip', engine='python')

print("Parsing complex fields")

def parse_column(col):
    try:
        return ast.literal_eval(col)
    except:
        return np.nan

df['histogram'] = df['histogram'].apply(parse_column)
df['byteentropy'] = df['byteentropy'].apply(parse_column)
df['strings'] = df['strings'].apply(parse_column)

print("Dropping rows that failed parsing")
df.dropna(subset=['histogram', 'byteentropy', 'strings'], inplace=True)

print("Flattening parsed fields")
histogram_df = pd.DataFrame(df['histogram'].tolist()).add_prefix("hist_")
byteentropy_df = pd.DataFrame(df['byteentropy'].tolist()).add_prefix("entropy_")
strings_df = pd.json_normalize(df['strings']).add_prefix("str_")

print("Combining and cleaning final feature set")
df_final = pd.concat([histogram_df, byteentropy_df, strings_df], axis=1)
df_final = df_final.select_dtypes(include=[np.number])

if df_final.empty:
    print("No valid samples found")
    exit()

expected_feature_count = 256
df_final = df_final.iloc[:, :expected_feature_count]
df_final.columns = [f"feature_{i}" for i in range(expected_feature_count)]

print("Running predictions")
predictions = model.predict(df_final)

df['prediction'] = predictions

# Add file hashes if filenames exist
if 'sha256' not in df.columns and 'filename' in df.columns:
    def compute_sha256(path):
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return "ERROR"
    df['sha256'] = df['filename'].apply(compute_sha256)

# Quarantining malicious files 
if 'filename' in df.columns:
    for i, row in df.iterrows():
        pred = row['prediction']
        file_path = row['filename']
        if pred in [1, -1] and os.path.isfile(file_path):
            try:
                basename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{timestamp}_{basename}"
                shutil.move(file_path, os.path.join(QUARANTINE_DIR, new_name))
            except Exception as e:
                print(f"⚠️ Failed to move {file_path}: {e}")

print("Saving results to predictions_output.csv")
df.to_csv(OUTPUT_CSV, index=False)

# Summary
from collections import Counter
counts = Counter(predictions)

print("\nPrediction summary:")
print(f"Benign (0): {counts.get(0, 0)}")
print(f"Malicious (1): {counts.get(1, 0)}")
print(f"Possibly Malicious (-1): {counts.get(-1, 0)}")
print(f"Output saved to {OUTPUT_CSV}")
