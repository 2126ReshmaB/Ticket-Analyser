from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import io
import ahocorasick
from one_class_svm import one_class_svm_ml
# from langchain_test_usecases import get_keywords_from_llm

 
app = Flask(__name__)
CORS(app)
 

# applications = get_keywords_from_llm()
applications = ["(SIEM)", "ACA", "AMI", "API", "APIs", "APM", "AWS", "Adobe", "AirDrop", "Airtable", "Amazon", "Analytics", "Ansible", "Anti-Malware", "Anti-Phishing", "Antivirus", "App", "Apps", "Argo", "Asana", "Auto-Analyze", "Auto-Compare", "Auto-Filter", "Auto-Flag", "Auto-Merge", "Auto-Notify", "Auto-Pre-Fill", "Auto-Renew", "Auto-Save", "Auto-Score", "Auto-Split", "Auto-Suggestion", "Auto-Summarize", "Auto-Translate", "Auto-Trigger", "AutoPlay", "Autopilot", "Azure", "Basecamp", "Beanstalk", "BigQuery", "BitLocker", "Boomerang", "Bot", "Browser", "Browsers", "CAD", "CASB", "CI", "CI/CD", "CMS", "CRM", "CRMs", "CSS/JS", "Cache", "Calendar", "Calendly", "Canva", "Chat", "Chatbot", "Chatbots", "Chocolatey", "Classroom", "ClickUp", "CloudFormation", "CloudFront", "CloudWatch", "Cortana", "Dashboard", "Databases", "Defender", "DevOps", "Docker", "Docs", "Dropbox", "Dynamics", "DynamoDB", "E-Learning", "E-Signature", "ERP", "Email", "Evernote", "Exchange", "Facebook", "FileVault", "Firebase", "Firewall", "Forms", "Framework", "Frameworks", "Freshdesk", "GIS", "Games", "Gamification", "Gamify", "Geo-Tracking", "GitHub", "Gmail", "Google", "HRMS", "HTTP/3", "HappyFox", "HelpDesk", "HelpDesk's", "Helpdesk", "HubSpot", "IAM", "IDEs", "IMAP", "ITIL", "ITSM", "Intune", "JIRA", "Jamf", "Java", "Jira", "Kayako", "Kerberos", "Kubernetes", "LDAP", "Lambda", "Library", "LinkedIn", "Linux", "Lists", "MDM", "MFA", "Mail", "Mailbox", "Mailchimp", "Malware", "Microsoft", "Monday.com", "MySQL", "NAS", "NetFlow", "Notification", "Notion", "Okta", "OneDrive", "OpenAI", "Organizer", "Outlook", "PDF", "PHP", "POP3", "Planner", "Playbook", "Plugin", "Plugins", "Portal", "Portals", "PowerShell", "Pro", "Project", "Pub/Sub", "QA", "QuickBooks", "Quiz", "RADIUS", "RDP", "RDS", "Ransomware", "Registry", "Repository", "S3", "SIEM", "SMS", "SMTP", "SQL", "SSH", "SSO", "SaaS", "Safari", "Salesforce", "Sandbox", "SaneArchive", "SaneBlackHole", "SaneCC", "SaneLater", "Scanner", "Scheduler", "Scripts", "Self-Hosted", "ServiceNow", "SharePoint", "Sheets", "Shopify", "Siri", "Slack", "Slides", "Software", "Spiceworks", "Splunk", "Spreadsheet", "Sudo", "Suite", "Superhuman", "TOTP", "Tableau", "Teams", "Terminal", "Terraform", "Ticketing", "Tracker", "Trello", "VPC", "VPN", "VPNs", "Vault", "Vaults", "VoIP", "WHOIS", "Watchtower", "WebSocket", "Webhook", "Webhooks", "WhatsApp", "Wiki", "Windows", "WordPress", "Workspace", "Yammer", "Zapier", "Zendesk", "Zoho", "Zoom", "analytics", "app", "chatbots", "iCloud", "iOS", "plugin", "plugins", "podcast", "syslog", "ticketing", "webhook", "wiki"]
 
ito_df = pd.DataFrame()
non_ito_df = pd.DataFrame()
 

def build_automaton():
    automaton = ahocorasick.Automaton()
    for kw in applications:
        automaton.add_word(kw.lower(), ("application", kw))
    automaton.make_automaton()
    return automaton
 

def classify(text, automaton):
    text = text.lower()
    found = set()
    for _, (typ, _) in automaton.iter(text):
        found.add(typ)
    return "ITO" if {"application"}.issubset(found) else "Non-ITO"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
 
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files allowed"}), 400
 
    content = file.read().decode('utf-8')
    df = pd.read_csv(io.StringIO(content))
 
    if 'Description' not in df.columns:
        return jsonify({"error": "CSV must have 'Description' column"}), 400
 
    automaton = build_automaton()
    df['Category'] = df['Description'].astype(str).apply(lambda x: classify(x, automaton))

    
    ito_df = df[df['Category'] == 'ITO']
    non_ito_df = df[df['Category'] == 'Non-ITO']

    ito_df.to_csv('regex_ito_tickets.csv',index=False)
    non_ito_df.to_csv('regex_non_ito_tickets.csv', index = False)

    one_class_svm_ml('regex_ito_tickets.csv')

    return {"message": "sucess"}, 200

@app.route("/get-ito-tickets", methods=['GET'])
def get_ito_ticekts():
    try:
        ito_df = pd.read_csv("ito_predictions.csv")
        return jsonify({
            "ito": ito_df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error" : str(e)}), 500
    
@app.route("/get-non-ito-tickets", methods=['GET'])
def get_non_ito_ticekts():
    try:
        non_ito_df = pd.read_csv("non_ito_predictions.csv")
        return jsonify({
            "non_ito": non_ito_df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error" : str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)