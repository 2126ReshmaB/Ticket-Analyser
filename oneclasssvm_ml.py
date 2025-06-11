import os

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.ensemble import IsolationForest

# === Step 1: Load ITO Descriptions Recursively ===

def load_ito_descriptions(folder_path):

    descriptions = []

    for root, _, files in os.walk(folder_path):

        for file in files:

            if file.endswith('.csv'):

                file_path = os.path.join(root, file)

                try:

                    df = pd.read_csv(file_path)

                    if 'Description' in df.columns:

                        desc = df['Description'].dropna().astype(str).tolist()

                        descriptions.extend(desc)

                except Exception as e:

                    print(f"⚠️ Failed to read {file_path}: {e}")

    return descriptions

# === Step 2: TF-IDF Vectorizer ===

def vectorize_text(corpus):

    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    X = vectorizer.fit_transform(corpus)

    return X, vectorizer

# === Step 3: Train Isolation Forest ===

def train_isolation_forest(X_train):

    model = IsolationForest(contamination=0.1, random_state=42)

    model.fit(X_train.toarray())

    return model

# === Step 4: Load & Vectorize Test Data ===

def load_test_data(file_path, vectorizer):

    test_df = pd.read_csv(file_path)

    test_df['Document'] = test_df['Document'].astype(str)

    X_test = vectorizer.transform(test_df['Document'])

    return test_df, X_test

# === Step 5: Save Predictions ===

def save_predictions(test_df, predictions):

    test_df['predicted_label'] = ['ITO' if p == 1 else 'Non-ITO' for p in predictions]

    ito_df = test_df[test_df['predicted_label'] == 'ITO']

    non_ito_df = test_df[test_df['predicted_label'] == 'Non-ITO']

    ito_df.to_csv("ito_predictions.csv", index=False)

    non_ito_df.to_csv("non_ito_predictions.csv", index=False)

    print(f"✅ ITO predictions saved to 'ito_predictions.csv' ({len(ito_df)} rows)")

    print(f"✅ Non-ITO predictions saved to 'non_ito_predictions.csv' ({len(non_ito_df)} rows)")

# === Main Script ===

# 🔁 Change these paths

ito_folder_path = "Usecases"

test_file_path = "regex_ito_tickets.csv"

# Step 1: Load training data

ito_descriptions = load_ito_descriptions(ito_folder_path)

# Step 2: Vectorize and train

X_train, tfidf_vectorizer = vectorize_text(ito_descriptions)

model = train_isolation_forest(X_train)

# Step 3: Load test and predict

test_df, X_test = load_test_data(test_file_path, tfidf_vectorizer)

predictions = model.predict(X_test.toarray())  # 1 = normal, -1 = anomaly

# Step 4: Save results

save_predictions(test_df, predictions)
 