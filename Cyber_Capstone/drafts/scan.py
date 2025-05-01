import os
import time
import pandas as pd
import joblib
import ast
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
WATCH_DIR = "to_scan" 
MODEL_PATH = "Infante_Antivirus_Model.joblib"
OUTPUT_LOG = "scan_log.csv"

# Load Model
print("Loading Infante Antivirus")
model = joblib.load(MODEL_PATH)

# Helper Functions
def parse_column(col):
    try:
        return ast.literal_eval(col)
    except:
        return np.nan

def clean_and_prepare_features(df):
    df['histogram'] = df['histogram'].apply(parse_column)
    df['byteentropy'] = df['byteentropy'].apply(parse_column)
    df['strings'] = df['strings'].apply(parse_column)

    df.dropna(subset=['histogram', 'byteentropy', 'strings'], inplace=True)

    histogram_df = pd.DataFrame(df['histogram'].tolist()).add_prefix("hist_")
    byteentropy_df = pd.DataFrame(df['byteentropy'].tolist()).add_prefix("entropy_")
    strings_df = pd.json_normalize(df['strings']).add_prefix("str_")

    df_final = pd.concat([histogram_df, byteentropy_df, strings_df], axis=1)
    df_final = df_final.select_dtypes(include=[np.number])
    df_final = df_final.iloc[:, :256]
    df_final.columns = [f"feature_{i}" for i in range(256)]

    return df_final

def predict_malware(file_path):
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
        df_clean = clean_and_prepare_features(df)
        predictions = model.predict(df_clean)
        label_counts = pd.Series(predictions).value_counts().to_dict()
        return predictions, label_counts
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None, {}

# File Watcher Handler
class ScanHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            print(f"🆕 New file detected: {event.src_path}")
            predictions, summary = predict_malware(event.src_path)
            if predictions is not None:
                result = {
                    "file": os.path.basename(event.src_path),
                    "summary": summary,
                    "timestamp": pd.Timestamp.now()
                }
                print(f"Scan complete: {result}")
                pd.DataFrame([result]).to_csv(OUTPUT_LOG, mode='a', header=not os.path.exists(OUTPUT_LOG), index=False)

# Start Watching
print(f" Watching directory: {WATCH_DIR}")
event_handler = ScanHandler()
observer = Observer()
observer.schedule(event_handler, WATCH_DIR, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()