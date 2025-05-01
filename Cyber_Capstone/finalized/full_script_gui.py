import pandas as pd
import joblib
import ast
import numpy as np
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Helper function to safely parse string representations of lists or dicts
def parse_column(col):
    try:
        return ast.literal_eval(col)  # Safely evaluate string literals
    except:
        return np.nan  # Return NaN if parsing fails

# Main antivirus logic. It loads model, processes file, runs predictions
def scan_and_quarantine(file_path, quarantine_folder=None):
    print("Loading Infante Antivirus")

    # Loads trained Random Forest model from disk
    model = joblib.load("Infante_Antivirus_Model.joblib")

    print("Loading selected CSV:", file_path)
    # Read the user-selected CSV, skipping bad lines
    df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')

    print("Parsing complex fields")
    # Parse embedded structures into actual Python objects
    df['histogram'] = df['histogram'].apply(parse_column)
    df['byteentropy'] = df['byteentropy'].apply(parse_column)
    df['strings'] = df['strings'].apply(parse_column)

    print("Dropping rows that failed parsing")
    # Remove rows where any of the parsed fields failed
    df.dropna(subset=['histogram', 'byteentropy', 'strings'], inplace=True)

    # Flatten nested features into individual numeric columns
    histogram_df = pd.DataFrame(df['histogram'].tolist()).add_prefix("hist_")
    byteentropy_df = pd.DataFrame(df['byteentropy'].tolist()).add_prefix("entropy_")
    strings_df = pd.json_normalize(df['strings']).add_prefix("str_")

    print("Combining and cleaning final feature set")
    # Merges all parsed feature data into a single DataFrame
    df_final = pd.concat([histogram_df, byteentropy_df, strings_df], axis=1)

    # Ensures only numeric features are kept
    df_final = df_final.select_dtypes(include=[np.number])

    expected_feature_count = 256
    if df_final.shape[1] < expected_feature_count:
        raise ValueError(f"Not enough features. Got {df_final.shape[1]}, expected {expected_feature_count}.")

    # Select and rename the first 256 numeric features to match model training format
    df_final = df_final.iloc[:, :expected_feature_count]
    df_final.columns = [f"feature_{i}" for i in range(expected_feature_count)]

    # Predict using the trained model
    predictions = model.predict(df_final)

    print("Preparing Results")
    # Map numeric predictions to labels
    label_mapping = {
        0: "Benign",
        1: "Malicious",
        -1: "Possibly Malicious"
    }
    labels = [label_mapping.get(pred, "Unknown") for pred in predictions]

    # Build a results DataFrame and save to disk
    result_df = pd.DataFrame({
        'Prediction': predictions,
        'Label': labels
    })
    result_df.to_csv("predictions_output.csv", index=False)

    # Count how many of each type of prediction
    summary = result_df['Label'].value_counts().to_dict()
    return result_df, summary

# Main GUI application using tkinter
class AntivirusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Infante Antivirus")
        self.geometry("500x450")
        self.configure(bg="#f0f0f0")

        self.file_path = None  # Path of selected file

        # Welcome label
        self.label = tk.Label(self, text="Welcome to Infante Antivirus", font=("Times New Roman", 18), bg="#f0f0f0")
        self.label.pack(pady=20)

        # Browse for a CSV file
        self.browse_button = tk.Button(self, text="Browse Cleaned CSV", command=self.browse_file, bg="#4169E1", fg="white", font=("Times New Roman", 12))
        self.browse_button.pack(pady=5)

        # Progress bar for user 
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Area to show scan results
        self.result_text = tk.Text(self, height=12, width=60, state="disabled")
        self.result_text.pack(pady=10)

        # Scan button
        self.scan_button = tk.Button(self, text="Start Scanning", command=self.start_scan, bg="#4169E1", fg="white", font=("Times New Roman", 12))
        self.scan_button.pack(pady=10)

    # Lets user select a file to scan
    def browse_file(self):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        selected_file = filedialog.askopenfilename(title="Select CSV File", filetypes=filetypes)
        if selected_file:
            self.file_path = selected_file
            self.result_text.configure(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Selected file: {selected_file}\n")
            self.result_text.configure(state="disabled")

    # Starts scanning when "Start Scanning" is clicked
    def start_scan(self):
        if not self.file_path:
            messagebox.showwarning("No file selected", "Please select a CSV file first.")
            return

        # Reset progress bar and results area
        self.progress["value"] = 0
        self.result_text.configure(state="normal")
        self.result_text.insert(tk.END, "Scan started...\n")
        self.result_text.configure(state="disabled")
        self.update()

        # Run scan in a new thread to keep GUI responsive
        threading.Thread(target=self.run_scan).start()

    # Runs the actual scan
    def run_scan(self):
        try:
            self.progress["value"] = 20
            self.update()

            # Optional quarantine folder (In development)
            quarantine_folder = "quarantine"
            results, summary = scan_and_quarantine(self.file_path, quarantine_folder)

            self.progress["value"] = 80
            self.update()

            # Show scan results in the GUI
            self.result_text.configure(state="normal")
            self.result_text.insert(tk.END, "\nScan Completed!\n\nSummary:\n")
            for label, count in summary.items():
                self.result_text.insert(tk.END, f"{label}: {count}\n")
            self.result_text.configure(state="disabled")

            self.progress["value"] = 100
            self.update()
        except Exception as e:
            # Show errors in a popup dialog
            messagebox.showerror("Error", str(e))

# Entry point
if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()
