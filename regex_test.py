import pandas as pd
import re
import os

root_folder = os.path.join(os.path.dirname(__file__), 'UseCases')

column_name = 'Short Description'
unique_words = set()

for foldername, _, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith('.csv') or filename.endswith('.xlsx'):
            file_path = os.path.join(foldername, filename)
            # print(file_path,end=" ")
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




df = pd.read_csv('all_tickets_processed_improved_v3.csv')

ito_patterns = list(unique_words)


ito_patterns_mod = re.compile("|".join(ito_patterns), re.IGNORECASE)

ito_tickets = []
non_ito_tickets = []

for index, row in df.iterrows():
    ticket = " ".join([str(cell) for cell in row.tolist() if pd.notnull(cell)])
    if(ito_patterns_mod.search(ticket)):
        ito_tickets.append(row)
    else:
        non_ito_tickets.append(row)

ito_df = pd.DataFrame(ito_tickets)
non_ito_df = pd.DataFrame(non_ito_tickets)

ito_df.to_csv("ITO_Tickets.csv", index = False)