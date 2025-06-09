import pandas as pd
import numpy as np
import string


import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

from sklearn.metrics import accuracy_score,classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from lightgbm import LGBMClassifier

def light_gbm_ml(ipo_file_name):
    nltk.download('stopwords')
    nltk.download('wordnet')

    warnings.filterwarnings('ignore')

    # read the Training CSV file
    df = pd.read_csv('all_tickets_processed_improved_v3.csv')
    # to remove duplicates
    df = df.dropna()

    # renaming the column names
    df.rename({'Document': 'tickets', 'Topic_group': 'topic'}, axis = 1, inplace= True)

    stop_words = set(stopwords.words('english'))
    lematizer = WordNetLemmatizer()

    # Data Pre-Processing
    def data_preprocess(text):
        # 1. Convert to LowerCase
        text = text.lower()
        # 2. Remove punctuations
        text = ''.join([c for c in text if c not in string.punctuation])
        # 3. split into words
        words = text.split()
        # 4. Remove stopwords
        words = [lematizer.lemmatize(w) for w in words if w not in stop_words and not w.isdigit()]
        return ' '.join(words)

    df['tickets'] = df['tickets'].apply(data_preprocess)

    # Data Encoder = Numbering the labels
    encoder = LabelEncoder()
    df['topic'] = encoder.fit_transform(df['topic'])


    x = df['tickets']
    y = df['topic']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('lgbm', LGBMClassifier())
    ])

    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("Classification report:\n", classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    label_map = dict(zip(encoder.transform(encoder.classes_), encoder.classes_))
    print("Label Mapping: ", label_map) 

    mapping_dict = {
    'Access': 'ITO',
    'Administrative rights': 'ITO',
    'HR Support': 'Non ITO',
    'Hardware': 'ITO',
    'Internal Project': 'Non ITO',
    'Miscellaneous': 'Rubbish',
    'Purchase': 'Non ITO',
    'Storage': 'ITO'
    }


    ito_tickets = []
    non_ito_tickets = []

    df = pd.read_csv(ipo_file_name)

    for index, row in df.iterrows():
        new_ticket = row['Document']
        predicted_lable_num = pipeline.predict([new_ticket])[0]

        predicted_lable_name = encoder.inverse_transform([predicted_lable_num])[0]
        if(mapping_dict.get(predicted_lable_name) == "ITO"):
            ito_tickets.append((row['Document'], "ITO"))
        else:
            non_ito_tickets.append((row['Document'], "Non ITO"))

    ito_df = pd.DataFrame(ito_tickets, columns=['Document','Topic_group'])
    non_ito_df = pd.DataFrame(non_ito_tickets, columns=['Document','Topic_group'])

    ito_df.to_csv('ml_ito_tickets.csv',index=False)
    non_ito_df.to_csv('ml_non_ito_tickets.csv', index = False)