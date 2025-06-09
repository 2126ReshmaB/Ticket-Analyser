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

mapping_dict = {
    'general': 'Rubbish',
    'Access': 'ITO',
    'Administrative rights': 'ITO',
    'HR Support': 'Non ITO',
    'Hardware': 'ITO',
    'Internal Project': 'Non ITO',
    'Miscellaneous': 'Rubbish',
    'Purchase': 'Non ITO',
    'Storage': 'ITO'
}



# df = pd.read_excel('Usecases/AM_AT/Asset Panda.xlsx')
# for index, row in df.iterrows():
#     new_ticket = row['Short Description']
#     predicted_lable_num = pipeline.predict([new_ticket])[0]

#     predicted_lable_name = encoder.inverse_transform([predicted_lable_num])[0]
#     print(new_ticket," ",mapping_dict.get(predicted_lable_name))