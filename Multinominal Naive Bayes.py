multinomial Naive Bayes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline
import warnings, string, nltk, random, gc, joblib
warnings.filterwarnings('ignore')
from sklearnex import patch_sklearn
patch_sklearn()
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from symspellpy import SymSpell, Verbosity
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
 
 
from tqdm.notebook import tqdm
tqdm.pandas()
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, ConfusionMatrixDisplay
from yellowbrick.classifier import ClassPredictionError
from sklearn.utils.class_weight import compute_class_weight
df = pd.read_csv('/content/all_tickets_processed_improved_v3.csv')
df.head()
f.rename({'Document': 'ticket_text', 'Topic_group': 'topic'},axis=1,inplace=True)
df['num_words'] = df.ticket_text.apply(len)
df.num_words.describe()
def preprocess_text(text):
    nopunc = [char.lower() for char in text if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return ' '.join([word for word in nopunc.split() if word not in stopwords.words('english') and not word.isdigit()])
symspell = SymSpell()
 
def fix_spelling_mistakes(text):
lemmatizer = WordNetLemmatizer()
 
def lemmatize_words(text):
    return ' '.join([lemmatizer.lemmatize(word) for word in text.split()]) 
    corrected_spellings = []
 
    for token in text.split():
        x = symspell.lookup(phrase=token,verbosity=Verbosity.CLOSEST,max_edit_distance=2,include_unknown=True)[0].__str__()
        y = x.split(',')[0]
        corrected_spellings.append(y)
 
    return ' '.join(corrected_spellings)
 
encoder = LabelEncoder()
df.topic = encoder.fit_transform(df.topic)
df.topic.value_counts()
encoded_labels = dict()
 
for idx, label in enumerate(encoder.classes_):
    encoded_labels[idx] = label
 
print(encoded_labels)
class_weights = compute_class_weight(class_weight='balanced',classes=np.unique(df.topic),y=df.topic)
class_weight_dict = dict(zip(np.unique(df.topic),class_weights))
class_weight_dict
X = df['ticket_text']
y = df['topic']
X.shape, y.shape
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True, random_state=101)
roc_auc_scores = []
model_names = []
accuracy_scores = []
precision_scores = []
recall_scores = []
f1_scores = []
 
# Make sure these lists exist before calling this function:
# model_names, accuracy_scores, precision_scores, recall_scores, f1_scores, roc_auc_scores
 
def train_and_evaluate_model(model, X_train, X_test, y_train, y_test):
    pipeline = Pipeline(steps=[
        ('tfidf', TfidfVectorizer()),
        ('model', model)
    ])
 
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
 
    # Some models (like MultinomialNB) support predict_proba
    try:
        y_pred_proba = pipeline.predict_proba(X_test)
    except AttributeError:
        y_pred_proba = None
 
    print("\n=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))
 
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred))
 
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
    plt.show()
 
    # ClassPredictionError plot (safe handling of missing classes)
    try:
        present_classes = np.unique(np.concatenate((y_test, y_pred)))
        model_classes = pipeline.named_steps['model'].classes_
        safe_classes = [cls for cls in model_classes if cls in present_classes]
 
        visualizer = ClassPredictionError(pipeline, classes=safe_classes)
        visualizer.fit(X_train, y_train)
        visualizer.score(X_test, y_test)
        visualizer.show()
    except Exception as e:
        print(f"[Warning] Skipping ClassPredictionError plot: {e}")
 
    # Metrics calculation
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
 
    # ROC AUC (only if y_pred_proba is available)
    if y_pred_proba is not None:
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba, average='weighted', multi_class='ovr')
        except ValueError:
            roc_auc = float('nan')
    else:
        roc_auc = float('nan')
 
    # Store results (make sure these lists are defined globally before use)
    model_names.append(str(model).split('(')[0])
    accuracy_scores.append(acc)
    precision_scores.append(prec)
    recall_scores.append(recall)
    f1_scores.append(f1)
    roc_auc_scores.append(roc_auc)
 
    gc.collect()
    return pipeline
mnb_pipeline = train_and_evaluate_model(MultinomialNB(), X_train, X_test, y_train, y_test)
model_perfs = pd.DataFrame({'Model': model_names,
                            'Accuracy': accuracy_scores,
                            'Precision': precision_scores,
                            'Recall': recall_scores,
                            'F1': f1_scores,
                            'ROC-AUC': roc_auc_scores}).sort_values('Accuracy',ascending=False).reset_index(drop=True)
model_perfs
 
import pandas as pd
 
# ✅ Custom mapping
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
 
#  Load Excel file
df_test = pd.read_excel('Usecases/AM_AT/Asset Panda.xlsx')
 
#  Label encoder mapping (inverse of label encoding)
label_map = dict(zip(encoder.transform(encoder.classes_), encoder.classes_))
print("Label Mapping: ", label_map)
 
#  Loop over test data and predict
for index, row in df_test.iterrows():
    new_ticket = row['Short Description']  # adjust column name if different
 
    # Predict using your trained pipeline
    predicted_label_num = mnb_pipeline.predict([new_ticket])[0]
    predicted_label_name = encoder.inverse_transform([predicted_label_num])[0]
 
    # Map predicted label to broader category
    mapped_category = mapping_dict.get(predicted_label_name, 'Unknown')
 
    # Output the result
    print(f"Ticket: {new_ticket}\n→ Predicted Label: {predicted_label_name} → Category: {mapped_category}\n")
 
