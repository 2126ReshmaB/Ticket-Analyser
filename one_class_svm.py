import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import OneClassSVM
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from langchain_test import llm_classification
    
def one_class_svm_ml(file_path):
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
                        print(f"Failed to read {file_path}: {e}")
        return descriptions

    def vectorize_text(corpus):
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = vectorizer.fit_transform(corpus)
        return X, vectorizer



    def train_one_class_svm(X_train):
        model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)
        model.fit(X_train)
        return model



    def load_test_data(file_path, vectorizer):
        test_df = pd.read_csv(file_path)
        test_df['Description'] = test_df['Description'].astype(str)
        X_test = vectorizer.transform(test_df['Description'])
        return test_df, X_test


    def save_predictions(test_df, predictions):
        test_df['predicted_label'] = ['ITO' if p == 1 else 'Non-ITO' for p in predictions]
        ito_df = test_df[test_df['predicted_label'] == 'ITO']
        non_ito_df = test_df[test_df['predicted_label'] == 'Non-ITO']
        ito_df.to_csv("ito_predictions.csv", index=False)
        non_ito_df.to_csv("non_ito_predictions.csv", index=False)
        print(f"ITO samples saved: {len(ito_df)} to 'ito_predictions.csv'")
        print(f"Non-ITO samples saved: {len(non_ito_df)} to 'non_ito_predictions.csv'")
        llm_classification()

    ito_folder_path = "Usecases"
    test_file_path = file_path

    ito_descriptions = load_ito_descriptions(ito_folder_path)
    X_train, tfidf_vectorizer = vectorize_text(ito_descriptions)
    svm_model = train_one_class_svm(X_train)

    test_df, X_test = load_test_data(test_file_path, tfidf_vectorizer)
    predictions = svm_model.predict(X_test)
    save_predictions(test_df, predictions)




    




 
