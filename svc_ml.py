import os
import re
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')  # To avoid LookupError

# Load CSV files recursively from a folder (for ITO data)
def load_csv_recursive(folder_path):
    data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
                except:
                    df = pd.read_csv(file_path, encoding='ISO-8859-1', on_bad_lines='skip')
                desc_col = next((col for col in df.columns if col.lower() == 'description'), None)
                if desc_col:
                    df = df[[desc_col]].dropna()
                    df.columns = ['Description']
                    data.append(df)
    return pd.concat(data, ignore_index=True) if data else pd.DataFrame(columns=['Description'])

# Text cleaning and tokenizing
stop_words = set(stopwords.words('english'))
def clean_and_tokenize(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', str(text).lower())
    tokens = word_tokenize(text)
    return [word for word in tokens if word not in stop_words]

# --- Step 1: Load ITO training data ---
ito_df = load_csv_recursive("Usecases")
if ito_df.empty:
    raise ValueError("❌ No ITO data found in the specified folder.")

ito_df['cleaned'] = ito_df['Description'].apply(lambda x: ' '.join(clean_and_tokenize(x)))
ito_df['label'] = 1  # ITO label

# --- Step 2: Create synthetic Non-ITO dataset with 200 rows ---
categories = [
    "HR", "Marketing", "Finance", "Customer Support", "Logistics",
    "Facilities", "Legal", "Sales", "Research", "Training"
]

descriptions = [
    "Employee payroll processing and salary calculation tasks.",
    "Campaign management for product launches and promotions.",
    "Budget planning and financial reporting for company accounts.",
    "Handling customer queries and resolving service issues.",
    "Managing warehouse inventory and shipment tracking processes.",
    "Maintenance of office premises and utility services.",
    "Contract reviews and compliance monitoring activities.",
    "Lead generation and client relationship management.",
    "Market research and competitor analysis for new products.",
    "Organizing employee skill development programs and workshops."
]

short_descriptions = [
    "Payroll processing", "Campaign management", "Financial reporting",
    "Customer service", "Inventory and shipment", "Office maintenance",
    "Contract compliance", "Lead and client management",
    "Market research", "Employee training"
]

# Generate 200 rows by repeating and varying
rows = []
for i in range(200):
    idx = i % len(categories)
    cat = categories[idx]
    desc = descriptions[idx]
    short_desc = short_descriptions[idx]
    # Slight variation: add a suffix to description every 10th row
    if i % 10 == 0:
        desc = desc + f" Task ID {i}"
    rows.append({
        "Category": cat,
        "Description": desc,
        "Short_Description": short_desc
    })

non_ito_df = pd.DataFrame(rows)
non_ito_df['cleaned'] = non_ito_df['Description'].apply(lambda x: ' '.join(clean_and_tokenize(x)))
non_ito_df['label'] = 0  # Non-ITO label

# --- Step 3: Combine ITO and Non-ITO data ---
train_df = pd.concat([ito_df, non_ito_df], ignore_index=True)
X_train = train_df['cleaned']
y_train = train_df['label']

print("Training data label distribution:")
print(y_train.value_counts())

# --- Step 4: Train classifier ---
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
    ('svc', LinearSVC())
])
pipeline.fit(X_train, y_train)

print("✅ Model training complete with ITO and synthetic Non-ITO data.")

# --- Step 5: Load mixed data for prediction ---
mixed_file_path = "ito_nonito_dataset.csv"
mixed_df = pd.read_csv(mixed_file_path)

desc_col = next((col for col in mixed_df.columns if col.lower() == 'description'), None)
if not desc_col:
    raise ValueError("❌ 'Description' column not found in the mixed file.")

mixed_df['cleaned'] = mixed_df[desc_col].apply(lambda x: ' '.join(clean_and_tokenize(x)))

# --- Step 6: Predict ---
mixed_df['prediction'] = pipeline.predict(mixed_df['cleaned'])

pred_ito = mixed_df[mixed_df['prediction'] == 1]
pred_non_ito = mixed_df[mixed_df['prediction'] == 0]

# --- Step 7: Save results ---
pred_ito[[desc_col]].to_csv("Predicted_ITO.csv", index=False)
pred_non_ito[[desc_col]].to_csv("Predicted_Non_ITO.csv", index=False)

print("✅ Classification done.")
print("📁 Saved: Predicted_ITO.csv")
print("📁 Saved: Predicted_Non_ITO.csv")