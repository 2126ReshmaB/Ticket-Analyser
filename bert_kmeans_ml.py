import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
 

TRAIN_DIR = "Usecases"
TEST_FILE = "regex_ito_tickets.csv"
TEXT_COLUMN = "Ticket"  
N_CLUSTERS = 2
MODEL_NAME = "all-MiniLM-L6-v2"
OUTPUT_FILE = "test_output_with_clusters.csv"

 
def load_all_text_from_folder(folder):
    texts = []
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            try:
                if file.endswith(".csv"):
                    df = pd.read_csv(path)
                elif file.endswith(".xlsx"):
                    df = pd.read_excel(path)
                else:
                    continue
                if TEXT_COLUMN in df.columns:
                    texts.extend(df[TEXT_COLUMN].dropna().astype(str).tolist())
            except Exception as e:
                print(f"Error reading {path}: {e}")
    return texts
 
def load_test_texts(file):
    if file.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported test file format")
    
    if TEXT_COLUMN not in df.columns:
        raise ValueError(f"{TEXT_COLUMN} column not found in test file")
    
    return df, df[TEXT_COLUMN].astype(str).tolist()
 
def main():
    print("📁 Loading training data...")
    train_texts = load_all_text_from_folder(TRAIN_DIR)
 
    print(f"✅ Loaded {len(train_texts)} training samples.")
 
    print("🔄 Loading BERT model...")
    model = SentenceTransformer(MODEL_NAME)
 
    print("🔢 Generating embeddings...")
    train_embeddings = model.encode(train_texts, show_progress_bar=True)
 
    print("Training KMeans...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    kmeans.fit(train_embeddings)
 
    print("Loading test data...")
    test_df, test_texts = load_test_texts(TEST_FILE)
    test_embeddings = model.encode(test_texts, show_progress_bar=True)
 
    print("Predicting clusters...")
    cluster_labels = kmeans.predict(test_embeddings)
    test_df["Cluster"] = cluster_labels
 
    print(f"Saving output to {OUTPUT_FILE}")
    test_df.to_csv(OUTPUT_FILE, index=False)
 
    print("Done.")
 
if __name__ == "__main__":
    main()