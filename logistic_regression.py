import string
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

nltk.download('stopwords')
nltk.download('wordnet')

warnings.filterwarnings("ignore")

# Load and clean main dataset
df = pd.read_csv('all_tickets_processed_improved_v3.csv')
df = df.dropna()
df.rename({'Document': 'ticket_text', 'Topic_group': 'topic'}, axis=1, inplace=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Text preprocessing function
def preprocess(text):
    text = str(text).lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words and not w.isdigit()]
    return ' '.join(words)

df['ticket_text'] = df['ticket_text'].apply(preprocess)

# Encode target labels
encoder = LabelEncoder()
df['topic'] = encoder.fit_transform(df['topic'])

x = df['ticket_text']
y = df['topic']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# Build and train the model pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('logreg', LogisticRegression(max_iter=1000, multi_class='auto', solver='lbfgs'))
])

pipeline.fit(x_train, y_train)
y_pred = pipeline.predict(x_test)

# Evaluation
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

# Mapping label numbers to actual topics
label_map = dict(zip(encoder.transform(encoder.classes_), encoder.classes_))
print("Label Mapping: ", label_map)

# Topic-to-category mapping
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

# Predict on external Excel data
df_new = pd.read_excel('Asset Panda.xlsx')
df_new['Processed Description'] = df_new['Short Description'].apply(preprocess)
df_new['Predicted Topic'] = pipeline.predict(df_new['Processed Description'])
df_new['Predicted Topic Name'] = encoder.inverse_transform(df_new['Predicted Topic'])
df_new['Simplified Label'] = df_new['Predicted Topic Name'].apply(lambda x: mapping_dict.get(x, 'Unknown'))

# Print results
for _, row in df_new.iterrows():
    print(row['Short Description'], " ", row['Simplified Label'])

# Save to Excel
df_new.to_excel("Asset_Panda_Predicted.xlsx", index=False)
print("\n Results saved to 'Asset_Panda_Predicted.xlsx'")
