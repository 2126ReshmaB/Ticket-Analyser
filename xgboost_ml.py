import string
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

from sklearn.metrics import accuracy_score,classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier


nltk.download('stopwords')
nltk.download('wordnet')

warnings.filterwarnings("ignore")

df = pd.read_csv('all_tickets_processed_improved_v3.csv')
df = df.dropna()

df.rename({'Document': 'ticket_text', 'Topic_group': 'topic'}, axis = 1, inplace= True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Data Cleaning
def preprocess(text):
    text = text.lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    words = text.split()

    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words and not w.isdigit()]
    return ' '.join(words)

df['ticket_text'] = df['ticket_text'].apply(preprocess)

# Data Encoding
encoder = LabelEncoder()
df['topic'] = encoder.fit_transform(df['topic'])


x = df['ticket_text']
y = df['topic']
print(x.shape)
print(y.shape)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('xgb', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'))
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
    'general': 'Rubbish',
    'Access': 'ITO',
    'Administrative rights': 'Non ITO',
    'HR Support': 'Non ITO',
    'Hardware': 'ITO',
    'Internal Project': 'Non ITO',
    'Miscellaneous': 'Rubbish',
    'Purchase': 'Non ITO',
    'Storage': 'ITO'
}


df = pd.read_csv('ito_nonito_dataset.csv')
for index, row in df.iterrows():
    new_ticket = row['Description']
    predicted_lable_num = pipeline.predict([new_ticket])[0]

    predicted_lable_name = encoder.inverse_transform([predicted_lable_num])[0]
    print(new_ticket," ",mapping_dict.get(predicted_lable_name))