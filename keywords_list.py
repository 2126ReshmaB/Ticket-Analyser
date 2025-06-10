import pandas as pd
import os

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lematizer = WordNetLemmatizer()

root_folder = os.path.join(os.path.dirname(__file__), 'UseCases')

column_name = 'Short Description'
unique_words = set()

def get_keywords():
    for foldername, subfoldername, filenames in os.walk(root_folder):
       for filename in filenames:
            if filename.endswith('.csv') or filename.endswith('.xlsx'):
                file_path = os.path.join(foldername, filename)
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif filename.endswith('xlsx'):
                        df = pd.read_excel(file_path)
                    if column_name not in df.columns:
                        print("not found")
                        continue
                    for row in df[column_name].dropna():
                        words = str(row).split()
                        for word in words:
                            unique_words.add(word.strip())
                except Exception as e:
                    print("file not found")

    words = list(unique_words) # 3354 Keywords
    words = [w for w in words if w not in stop_words and not w.isdigit()] 
    return words  # 3331 Keywords

print(get_keywords())