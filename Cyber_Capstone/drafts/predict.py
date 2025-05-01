import pandas as pd
import joblib
import ast
import numpy as np
import collections

print("Loading Infante Antivirus")
model = joblib.load("Infante_Antivirus_Model.joblib")

print("Loading cleaned_features.csv")
df = pd.read_csv("cleaned_features.csv", on_bad_lines='skip', engine='python')

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

if df_final.shape[1] < expected_feature_count:
    print(f"Not enough features to match the model. Got {df_final.shape[1]}, expected {expected_feature_count}")
    exit()

df_final = df_final.iloc[:, :expected_feature_count]
df_final.columns = [f"feature_{i}" for i in range(expected_feature_count)]

if hasattr(model, "feature_names_in_") and len(model.feature_names_in_) != df_final.shape[1]:
    print(f"Feature mismatch: model expects {len(model.feature_names_in_)} features, but got {df_final.shape[1]}")
    exit()

print("Running predictions")
predictions = model.predict(df_final)

df_results = df.copy()
df_results["Prediction"] = predictions

# Map to readable labels
label_map = {
    0: "Benign",
    1: "Malicious",
    -1: "Possibly Malicious"
}
df_results["Label"] = df_results["Prediction"].map(label_map)

print("Saving results to predictions_output.csv")
df_results.to_csv("predictions_output.csv", index=False)

# Print summary
summary = collections.Counter(predictions)
print("\nPrediction summary:")
print(f"Benign (0): {summary.get(0, 0):,}")
print(f"Malicious (1): {summary.get(1, 0):,}")
print(f"Possibly Malicious (-1): {summary.get(-1, 0):,}")
print("Output saved to predictions_output.csv")
