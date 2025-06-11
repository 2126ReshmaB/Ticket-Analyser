import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam
# === Step 1: Load ITO Descriptions Recursively ===
def load_ito_descriptions(folder_path):
   descriptions = []
   for root, _, files in os.walk(folder_path):
       for file in files:
           file_path = os.path.join(root, file)
           try:
               if file.endswith('.csv'):
                   df = pd.read_csv(file_path)
               elif file.endswith('.xlsx'):
                   df = pd.read_excel(file_path)
               else:
                   continue
               if 'Description' in df.columns:
                   desc = df['Description'].dropna().astype(str).tolist()
                   descriptions.extend(desc)
           except Exception as e:
               print(f"⚠️ Failed to read {file_path}: {e}")
   return descriptions
# === Step 2: TF-IDF Vectorizer ===
def vectorize_text(corpus):
   vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
   X = vectorizer.fit_transform(corpus).toarray()
   return X, vectorizer
# === Step 3: Train Autoencoder ===
def train_autoencoder(X):
   input_dim = X.shape[1]
   input_layer = Input(shape=(input_dim,))
   encoded = Dense(64, activation="relu")(input_layer)
   encoded = Dense(32, activation="relu")(encoded)
   decoded = Dense(64, activation="relu")(encoded)
   decoded = Dense(input_dim, activation="sigmoid")(decoded)
   autoencoder = Model(inputs=input_layer, outputs=decoded)
   autoencoder.compile(optimizer=Adam(0.001), loss='mse')
   autoencoder.fit(X, X, epochs=100, batch_size=8, verbose=1)
   reconstructions = autoencoder.predict(X)
   mse = np.mean(np.power(X - reconstructions, 2), axis=1)
   threshold = np.percentile(mse, 95)
   return autoencoder, threshold
# === Step 4: Predict on Test Data ===
def predict_test_file(test_file_path, vectorizer, model, threshold):
   if test_file_path.endswith('.csv'):
       test_df = pd.read_csv(test_file_path)
   elif test_file_path.endswith('.xlsx'):
       test_df = pd.read_excel(test_file_path)
   else:
       raise Exception("Unsupported test file format")
   if 'description' not in test_df.columns:
       raise Exception("No 'description' column in test file")
   test_df['Description'] = test_df['Description'].astype(str)
   X_test = vectorizer.transform(test_df['Description']).toarray()
   reconstructions = model.predict(X_test)
   mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)
   predictions = ['ITO' if e <= threshold else 'Non-ITO' for e in mse]
   test_df['predicted_label'] = predictions
   # Save to separate files
   test_df[test_df['predicted_label'] == 'ITO'].to_csv("ito_predictions.csv", index=False)
   test_df[test_df['predicted_label'] == 'Non-ITO'].to_csv("non_ito_predictions.csv", index=False)
   print("✅ Saved 'ito_predictions.csv' and 'non_ito_predictions.csv'")
# === Main ===
# 🔁 Replace with your actual paths
train_folder_path = "/path/to/ito/folder"
test_file_path = "/path/to/test_file.csv"
# Load and train
ito_descriptions = load_ito_descriptions(train_folder_path)
X, vectorizer = vectorize_text(ito_descriptions)
model, threshold = train_autoencoder(X)
# Predict and save results
predict_test_file(test_file_path, vectorizer, model, threshold)