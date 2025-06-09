import os
import re
import pandas as pd
import ahocorasick

# === Define ITO-related keywords ===
ito_keywords = [
    "server", "network", "firewall", "cpu usage", "latency",
    "load balancer", "dns", "database", "application", "memory leak"
]

# === Compile regex for keyword matching ===
regex_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, ito_keywords)) + r')\b', re.IGNORECASE)

# === Build Aho-Corasick Automaton ===
def build_automaton(keywords):
    A = ahocorasick.Automaton()
    for idx, keyword in enumerate(keywords):
        A.add_word(keyword.lower(), (idx, keyword))
    A.make_automaton()
    return A

automaton = build_automaton(ito_keywords)

# === Function to classify a single line of text ===
def classify_text(text):
    text_lower = text.lower()

    for _, (_, keyword) in automaton.iter(text_lower):
        return "ITO"

    if regex_pattern.search(text_lower):
        return "ITO"

    return "Non-ITO"

# === Recursively process folder and classify lines ===
def classify_folder(root_folder):
    ito_data = []
    non_ito_data = []

    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(('.txt', '.csv')):
                file_path = os.path.join(foldername, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        lines = file.readlines()
                        for line in lines:
                            line = line.strip()
                            if line:
                                label = classify_text(line)
                                row = {
                                    'file': file_path,
                                    'line': line,
                                    'label': label
                                }
                                if label == "ITO":
                                    ito_data.append(row)
                                else:
                                    non_ito_data.append(row)
                except Exception as e:
                    print(f"❌ Failed to process {file_path}: {e}")
    
    # Convert to DataFrames
    df_ito = pd.DataFrame(ito_data)
    df_non_ito = pd.DataFrame(non_ito_data)

    # Save both files
    df_ito.to_csv("ito_classified.csv", index=False)
    df_non_ito.to_csv("non_ito_classified.csv", index=False)

    print("✅ Done. Files saved as 'ito_classified.csv' and 'non_ito_classified.csv'.")

# === Example usage ===
folder_path = "/path/to/your/folder"  # 🔁 Replace with actual path
classify_folder(folder_path)