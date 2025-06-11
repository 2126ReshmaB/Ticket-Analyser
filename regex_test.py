from keywords_list import get_keywords
from lgbm_ml import light_gbm_ml
from keywords_list import get_keywords
from langchain_test_usecases import get_keywords_from_llm

import pandas as pd
import ahocorasick
import os

actions, applications, objects = get_keywords_from_llm()
print(actions)



# root_folder = os.path.join(os.path.dirname(__file__), 'UseCases')

# keywords = ['server', 'vpn', 'firewall', 'latency', 'ssl', 'ssl/tls', 'ftp', 'active directory', 'ad',
#     'iam', 'rds', 'directory', 'network', 'router', 'switch', 'vm', 'hypervisor', 'latency',
#     'downtime', 'outage', 'printer', 'infrastructure', 'cloud', 'azure', 'aws', 'linux',
#     'windows server', 'bitlocker', 'incident', 'siem', 'logging', 'logs', 'monitor', 'restore',
#     'backup', 'backups', 'deployment', 'scaling', 'ports', 'inbound', 'outbound', 'load balancer',
#     'ip', 'dns', 'dhcp', 'tls', 'certificate', 'device', 'patch', 'vulnerability', 'asset', 'hostname',
#     'command', 'disk', 'memory', 'cpu', 'database', 'sql', 'mysql', 'oracle', 'postgresql',
#     'connectivity', 'access denied', 'unauthorized', 'proxy', 'failover', 'data center',
#     'infrastructure issue', 'security', 'compliance', 'endpoint', 'antivirus', 'malware', 'spyware',
#     'scan', 'power outage', 'hardware', 'bios', 'firmware', 'network outage', 'internet issue',
#     'wifi', 'ethernet', 'connectivity issue', 'install patch', 'update patch', 'system reboot']

def build_automaton(actions, applications, objects):
    # Creates plain Trie
    automaton = ahocorasick.Automaton()
    for kw in actions:
        automaton.add_word(kw.lower(), ("action", kw))
    for kw in applications:
        automaton.add_word(kw.lower(), ("application", kw))
    for kw in objects:
        automaton.add_word(kw.lower(), ("object", kw))
    automaton.make_automaton()
    return automaton

def classify_ticket(ticket, automaton):
    ticket = ticket.lower()
    found_categories = set()

    for _, (category, keyword) in automaton.iter(ticket):
        found_categories.add(category)
    
    if {'action', 'application', 'object'}.issubset(found_categories):
        return "ITO"
    else:
        return "Non-ITO"

df = pd.read_csv('sample_tickets.csv')
automaton = build_automaton(actions, applications, objects)

ito_tickets = []
non_ito_tickets = []

for ticket in df['Description'].astype(str):
    category = classify_ticket(ticket, automaton)
    if category == 'ITO':
        ito_tickets.append((ticket, category))
    else:
        non_ito_tickets.append((ticket, category))


# This is for testing usecase folder

# for foldername, subfoldername, filenames in os.walk(root_folder):
#        for filename in filenames:
#             if filename.endswith('.csv') or filename.endswith('.xlsx'):
#                 file_path = os.path.join(foldername, filename)
#                 try:
#                     if filename.endswith('.csv'):
#                         df = pd.read_csv(file_path)
#                     elif filename.endswith('.xlsx'):
#                         df = pd.read_excel(file_path)

#                     for ticket in df['Description'].astype(str):
#                         category = classify_ticket(ticket, automaton)
#                         if category == 'ITO':
#                             ito_tickets.append((ticket, category))
#                         else:
#                             non_ito_tickets.append((ticket, category))
#                 except Exception as e:
#                     print("file not found")


ito_df = pd.DataFrame(ito_tickets, columns=['Document','Category'])
non_ito_df = pd.DataFrame(non_ito_tickets, columns=['Document','Category'])

ito_df.to_csv('regex_ito_tickets.csv',index=False)
non_ito_df.to_csv('regex_non_ito_tickets.csv', index = False)




light_gbm_ml('regex_ito_tickets.csv')























# df = pd.read_csv('all_tickets_processed_improved_v3.csv')

# ito_patterns = list(unique_words)


# ito_patterns_mod = re.compile("|".join(ito_patterns), re.IGNORECASE)

# ito_tickets = []
# non_ito_tickets = []

# for index, row in df.iterrows():
#     ticket = " ".join([str(cell) for cell in row.tolist() if pd.notnull(cell)])
#     if(ito_patterns_mod.search(ticket)):
#         ito_tickets.append(row)
#     else:
#         non_ito_tickets.append(row)

# ito_df = pd.DataFrame(ito_tickets)
# non_ito_df = pd.DataFrame(non_ito_tickets)

# ito_df.to_csv("ITO_Tickets.csv", index = False)