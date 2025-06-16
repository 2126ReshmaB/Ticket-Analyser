# Ticket Analzer (ITO vs Non-ITO)

This project classifies IT support tickets as **ITO** or **Non-ITO**:

1. **Aho-Corasick** for fast keyword matching
2. **TF-IDF + One-Class SVM** for anomaly/outlier detection
3. **LLM** for ambiguous tickets


## Requirements

- flask
- flask-cors
- pandas
- scikit-learn
- TfidfVectorizer
- OneClassSVM
- numpy
- ahocorasick
- AzureChatOPENAI
- nltk
- tqdm


## How to Run
    git clone https://github.com/yourusername/ticket-classifier.git

    Run Flask App
    -------------
        python upload_file.py
        
        Visit the app at:
            http://localhost:5000
        
    Run the React APP
    -----------------
        cd my-react-app
        npm run dev
        
        Visit the app at:
            http://localhost:5173
