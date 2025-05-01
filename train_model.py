import pandas as pd
import numpy as np
import ast
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("Loading data")

# Load the cleaned feature dataset
df = pd.read_csv('cleaned_features.csv', on_bad_lines='skip')
print("Data loaded, shape:", df.shape)

# Determines whether or not the second column contains stringified Python lists
sample_value = df.iloc[0, 1]
if isinstance(sample_value, str) and sample_value.startswith('['):
    print("Expanding features")
    
    # Parse the stringified list into a Python list
    df['features'] = df.iloc[:, 1].apply(ast.literal_eval)

    # Convert the list into a DataFrame with one column per feature
    feature_df = pd.DataFrame(df['features'].to_list())
    feature_df.columns = [f'feature_{i}' for i in range(feature_df.shape[1])]

    # Combine with the label column
    df = pd.concat([df['label'], feature_df], axis=1)
else:
    print("Features are already expanded.")

# Separate features (X) from labels (y)
X = df.drop(columns='label')
y = df['label']

# Making sure all values are numeric and fill any missing data with 0
X = X.apply(pd.to_numeric, errors='coerce')
X.fillna(0, inplace=True)

# Split the data into training and test sets
print("Training Random Forest Classifier")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate the model on the test set
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save the trained model for future use
joblib.dump(clf, 'Infante_Antivirus_Model.joblib')
print("Saved Infante_Antivirus_Model.joblib")

