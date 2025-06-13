from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import io
import ahocorasick
import zipfile
 
app = Flask(__name__)
CORS(app)
 
# Define keywords
objects = ["(ITSM)", "AMIs", "Access", "Account", "Address", "Administration", "Agent", "Agents", "Algorithms", "Alignment", "Always", "Apple", "Application", "Approvals", "Array", "Arrays", "Asset", "Assets", "Assignment", "Attachments", "Attacks", "Attempt", "Audio", "Audits", "Auto-Apply", "Automotive", "BIOS", "Badge", "Balancer", "Balancers", "Balancing", "Barcode", "Battery", "Bidding", "Blacklisting", "Bloatware", "Blockchain", "Blocklist", "Blocks", "Bluetooth", "Bots", "Brute-Force", "CDN", "CMDB", "CPU", "Calendar", "Calls", "Camera", "Campaigns", "Card", "Certificate", "Certification", "Charitable", "Chart", "Checklist", "Checks", "Client", "Clients", "Clipboard", "Cloud", "Cluster", "Clusters", "Command-Line", "Complexity", "Compliance", "Components", "Computational", "Computer", "Conferencing", "Connection", "Contacts", "Container", "Containers", "Contractors", "Control", "Cost", "Credential", "Credentials", "Cross-Time", "Culture", "Cycles", "DHCP", "DLL", "DNS", "Database", "Deadlines", "Deployments", "Desk", "Desktop", "Detection", "Developer", "Device", "Device-Based", "Devices", "Directory", "Disability", "Disaster", "Disk", "Dock", "Document", "Documents", "Domain", "Domains", "Drive", "Driver", "Drivers", "Drives", "Droplet", "Droplets", "Duplicates", "EBS", "EC2", "ELB", "Editors", "Emails", "Emulators", "Encrypted", "Encryption", "Endpoint", "Enterprise", "Environment", "Environments", "Equipment", "Exceptions", "Experience", "Expired", "Expiry", "FTP", "Fields", "File", "Files", "Fingerprint", "Firewalls", "Firmware", "Folder", "GPO", "Game", "Geo-blocking", "Geofencing", "Group", "HBAC", "HDDs", "HTTP", "HTTP/2", "HTTPS", "Hardware", "Header", "Hidden", "High", "Hub", "Hypervisor", "IDs", "IOPS", "IP", "IPs", "IT", "Identity", "Image", "In-App", "Incident", "Infrastructure", "Insider", "Interface", "Internet", "Inventory", "Invites", "IoT", "Issuance", "Journal", "KV", "Keylogger", "Keys", "Kiosk", "Learning", "Lease", "License", "Licensing", "Links", "List", "Log", "Logins", "Logon", "Logs", "Machine", "Machines", "Manager", "Mapping", "Meetings", "Memory", "Metric", "Metrics", "Milestone", "Mobile", "Modules", "Monitors", "Multimedia", "NAT", "NFC", "Namespace", "Net", "Network", "Networking", "Networks", "Noise", "OS", "Object", "Offices", "Operational", "Organization", "Overlap", "PCI", "PIN", "Package", "Packet", "Page", "Pages", "Partition", "Partitions", "Passkeys", "Password", "Patch", "Patches", "Path", "Payroll", "Paystub", "Peripherals", "Permissions", "Personal", "Physical", "Pipeline", "Pod", "Point", "Policy", "Port", "Portable", "Ports", "Pre-backup", "Printer", "Printers", "Privilege", "Promoter", "Proxies", "Proxy", "QR", "Quarantine", "Queue", "Quotas", "RAID", "Reader", "Realm", "Recording", "Relationships", "Replica", "Reports", "Repositories", "Robotics", "Role", "Roles", "Rooms", "SAN", "SCIM", "SLAs", "SNMP", "SSDs", "SSL", "SSL/TLS", "Scanners", "Screen", "Secret", "Segregation", "Sensor", "Server", "Servers", "Settings", "Shield", "Shout-Out", "Signature", "Site", "Soon", "Spanner", "Spreadsheets", "Storage", "Stream", "Stripe", "Summary", "System", "TTL", "Tables", "Tabs", "Task", "Text", "Thread", "Threats", "Ticket", "Tickets", "Tier", "Timer", "Token", "Tokens", "Tools", "Traffic", "Trash", "Tunnel", "Two-Factor", "URL", "URLs", "USB", "Users", "Utilities", "VM", "Vaulting", "Violation", "Volunteer", "Vulnerability", "WAF", "WAN", "Wallpaper", "Watch", "Watchers", "Website", "Websites", "Wi-Fi", "Window", "Workbooks", "Workflows", "Workplace", "Workspaces", "YubiKey", "Zones", "accounting", "accounts", "activities", "address", "agendas", "agent", "agents", "alarm", "apps", "array", "asset", "attachment", "audiences", "auto-reply", "automation", "balancers", "bastion", "battery", "blog", "board", "breaches", "browser", "bucket", "cache", "calculator", "cart", "center", "certificate", "certificates", "channels", "chat", "checklist", "checklists", "claims", "classrooms", "client", "cloud", "cluster", "collaborations", "connection", "connections", "contacts", "container", "cookie", "courses", "coverage", "critical", "dashboard", "dashboards", "data", "database", "databases", "demos", "department", "desk", "desktop", "device", "devices", "directory", "disk", "document", "documents", "domain", "domains", "drafts", "dual-screen", "duplication", "edge", "education", "email", "email-to-calendar", "emails", "endpoint", "endpoints", "entertainment", "environments", "fairs", "favicon", "features", "files", "firewall", "firewalls", "firmware", "folder", "folders", "follow-ups", "funnel", "gateway", "gateways", "guest", "habit", "hardware", "historical", "home", "host", "hosts", "house", "hub", "hubs", "iPads", "image", "immersive", "inbox", "inboxes", "infrastructure", "inquiries", "inspiration", "instance", "instances", "interface", "inventory", "issues", "journey", "keyboard", "keys", "license", "licenses", "lines", "link", "links", "lists", "live", "logs", "machines", "malware", "maps", "media", "memberships", "milestones", "mobile", "monitor", "multi-department", "network", "networking", "networks", "notes", "objects", "office", "order", "package", "packages", "page", "password", "permissions", "pipeline", "pod", "point", "port", "portal", "portals", "preparation", "printer", "programs", "project", "protocols", "proxies", "proxy", "queries", "queues", "quota", "reader", "receipts", "recipient", "redirection", "reference", "refund", "registries", "replica", "reports", "repositories", "repository", "reservations", "resolutions", "screens", "script", "seasonal", "security", "server", "serverless", "servers", "service", "session", "settings", "sign-up", "signatures", "simultaneously", "sitemap", "sitemaps", "sites", "snapshot", "snapshots", "spreadsheets", "stacks", "stages", "statistics", "storage", "student", "submissions", "subnets", "subscriber", "subscriptions", "system", "systems", "tables", "tags", "talent", "team-building", "templates", "thread", "ticket", "tickets", "token", "touch-screen", "tracker", "traffic", "travel", "unwanted", "urgent", "variables", "version", "video", "virtualization", "virus", "visitor", "volume", "web", "website", "websites", "whiteboard", "windows", "work", "workloads", "zones"]
actions = ["Add", "Addition", "Analyze", "Apply", "Approval", "Archival", "Archived", "Assessments", "Assign", "Attach", "Auditing", "Auto-Approve", "Auto-Calculate", "Auto-Categorize", "Auto-Clean", "Auto-Clear", "Auto-Close", "Auto-Combine", "Auto-Create", "Auto-Detect", "Auto-Enroll", "Auto-Escalate", "Auto-Export", "Auto-Fill", "Auto-Generate", "Auto-Highlight", "Auto-Populate", "Auto-Redirect", "Auto-Remove", "Auto-Schedule", "Auto-Send", "Auto-Set", "Auto-Sort", "Auto-Sync", "Auto-Tag", "Auto-Validate", "Auto-scale", "Autofill", "Automate", "Automated", "Backups", "Binding", "Blacklist", "Blocking", "Boot", "Build", "Bypass", "Calculation", "Change", "Check", "Check-In", "Check-In/Check-Out", "Check-Ins", "Checking", "Checkout", "Clean", "Cleanup", "Clear", "Clearing", "Clone", "Close", "Closure", "Collaborate", "Collect", "Combine", "Commit", "Comparison", "Compress", "Conduct", "Configure", "Conversion", "Coordinate", "Correct", "Create", "Customize", "Deactivate", "Deactivation", "Deallocation", "Debugging", "Decommissioning", "Delete", "Deletion", "Deploy", "Deprovisioning", "Design", "Detect", "Develop", "Disable", "Disposal", "Dispute", "Distribute", "Disturb", "Do", "Downgrade", "Download", "Downloads", "Drop", "Duplicate", "Editing", "Enable", "Enforce", "Enforced", "Enhance", "Enroll", "Ensure", "Escalate", "Exceeded", "Exit", "Export", "Extraction", "Facilitate", "Filing", "Filter", "Filtering", "Fix", "Focus", "Follow-Up", "Formatting", "Forwarding", "Generate", "Grant", "Grouping", "Handle", "Handles", "Handling", "Hardening", "Hire", "Hunting", "Identify", "Implementation", "Import", "Improve", "Indexing", "Install", "Installed", "Integrate", "Integration", "Investigation", "Isolation", "Keep", "Launch", "Leave", "Limiting", "Load", "Logging", "Login", "Logout", "Maintain", "Maintenance", "Manage", "Measure", "Mention", "Merge", "Migrate", "Mining", "Modification", "Monitoring", "Moves", "Normalization", "Notify", "Obfuscation", "Open", "Operating", "Optimize", "Orchestrate", "Organize", "Parsing", "Partitioning", "Pay", "Perform", "Personalize", "Plan", "Planning", "Polling", "Pooling", "Posting", "Preparation", "Prevent", "Printing", "Prioritization", "Prioritize", "Processing", "Protect", "Provide", "Provision", "Provisioning", "Publishing", "Pull", "Purchase", "Purge", "Push", "Querying", "Rationalization", "Read", "Reading", "Reallocation", "Reboot", "Reboots", "Receive", "Reclamation", "Reconnection", "Record", "Recover", "Recovery", "Recruitment", "Recycling", "Redirect", "Redirection", "Reduce", "Refill", "Refresh", "Registration", "Rejected", "Release", "Remediate", "Remediation", "Removal", "Remove", "Renaming", "Reopen", "Reopened", "Replace", "Replacement", "Request", "Research", "Reset", "Resets", "Resolved", "Restart", "Restarts", "Restore", "Restores", "Restrict", "Restructuring", "Retrieval", "Retry", "Reuse", "Reverse", "Review", "Rollback", "Rollbacks", "Rollout", "Rotate", "Rotation", "Run", "Sanitization", "Save", "Scaling", "Scan", "Search", "Secure", "Self-Destruct", "Send", "Separate", "Set", "Setup", "Share", "Sharing", "Shift", "Shredding", "Shutdown", "Sign-On", "Simulate", "Sleep", "Sort", "Sorting", "Split", "Splitting", "Standardize", "Start", "Streamline", "Support", "Supporting", "Suppression", "Sync", "Synchronization", "Synchronize", "Syncing", "Tagging", "Testing", "Thank", "Toggle", "Tracing", "Track", "Train", "Transfer", "Translation", "Tuning", "Unbinding", "Uninstall", "Unlock", "Unlocking", "Unlocks", "Unsubscribe", "Update", "Upgrade", "Upload", "Uploads", "Use", "Utilize", "Validate", "Verification", "Verify", "Visualization", "Visualize", "Wait", "Watermarking", "Wipe", "access", "addition", "alerting", "analysis", "analyze", "archive", "assessments", "assignment", "audit", "auto-healing", "auto-replies", "auto-scaling", "backup", "booking", "bounce", "building", "builds", "capture", "categorization", "categorize", "changes", "check", "cleaning", "cleanup", "clearing", "click", "cloning", "clustering", "coding", "collaboratively", "collect", "comparison", "compression", "conferencing", "conversion", "copied", "correction", "creation", "cross-selling", "decommissioning", "deleted", "deletion", "deletions", "deliverability", "deployments", "deprovisioning", "design", "detect", "detection", "direct", "discovery", "distribution", "download", "drag-and-drop", "duplicate", "efficiently", "enable", "enrollment", "execute", "execution", "export/export", "exports", "failover", "filing", "filtering", "fix", "flagging", "follow-up", "forwarder", "forwarders", "forwarding", "fulfillment", "functions", "grant", "handling", "handovers", "hardening", "help", "hosting", "improvement", "indexing", "initiation", "installation", "installations", "instantly", "launch", "launches", "lead", "learning", "linking", "lock", "logging", "login", "maintenance", "manage", "managed", "mapping", "measure", "meeting", "mentions", "merge", "merging", "migration", "migrations", "notifications", "onboarding", "open", "opens", "organize", "orphaned", "pagination", "parked", "patches", "patching", "pause", "planning", "pre-send", "predict", "prevention", "preview", "prioritize", "process", "propagation", "provisioning", "query", "read", "reassignment", "reboots", "record", "recovery", "recruitment", "redirects", "remediation", "remotely", "removal", "renewal", "reopen", "repeat", "repetitive", "replication", "replies", "reply", "reporting", "research", "reset", "resets", "resizing", "resolution", "restart", "restoration", "restore", "restrictions", "retries", "retrieval", "return", "reverse", "review", "revocation", "rollback", "rollbacks", "routing", "scale", "scan", "scanning", "scans", "scheduling", "scriptwriting", "search", "secure", "send", "sending", "sent", "separate", "separation", "setup", "share", "sharing", "signup", "snooze", "snoozing", "sorting", "spend", "split", "start/stop", "strategically", "submission", "suggest", "sustainability", "swipe", "switching", "sync", "syncing", "tagging", "targeting", "teardown", "termination", "testing", "track", "tracking", "training", "transcription", "transcriptions", "transfer", "tuning", "undo", "uninstall", "unsubscribe", "updates", "upgrade", "upgrades", "upload", "uploads", "upsell", "upselling", "using", "utilization", "validation", "verification", "versioning", "via", "waiting", "whitelisting", "write"]
applications = ["(SIEM)", "ACA", "AMI", "API", "APIs", "APM", "AWS", "Adobe", "AirDrop", "Airtable", "Amazon", "Analytics", "Ansible", "Anti-Malware", "Anti-Phishing", "Antivirus", "App", "Apps", "Argo", "Asana", "Auto-Analyze", "Auto-Compare", "Auto-Filter", "Auto-Flag", "Auto-Merge", "Auto-Notify", "Auto-Pre-Fill", "Auto-Renew", "Auto-Save", "Auto-Score", "Auto-Split", "Auto-Suggestion", "Auto-Summarize", "Auto-Translate", "Auto-Trigger", "AutoPlay", "Autopilot", "Azure", "Basecamp", "Beanstalk", "BigQuery", "BitLocker", "Boomerang", "Bot", "Browser", "Browsers", "CAD", "CASB", "CI", "CI/CD", "CMS", "CRM", "CRMs", "CSS/JS", "Cache", "Calendar", "Calendly", "Canva", "Chat", "Chatbot", "Chatbots", "Chocolatey", "Classroom", "ClickUp", "CloudFormation", "CloudFront", "CloudWatch", "Cortana", "Dashboard", "Databases", "Defender", "DevOps", "Docker", "Docs", "Dropbox", "Dynamics", "DynamoDB", "E-Learning", "E-Signature", "ERP", "Email", "Evernote", "Exchange", "Facebook", "FileVault", "Firebase", "Firewall", "Forms", "Framework", "Frameworks", "Freshdesk", "GIS", "Games", "Gamification", "Gamify", "Geo-Tracking", "GitHub", "Gmail", "Google", "HRMS", "HTTP/3", "HappyFox", "HelpDesk", "HelpDesk's", "Helpdesk", "HubSpot", "IAM", "IDEs", "IMAP", "ITIL", "ITSM", "Intune", "JIRA", "Jamf", "Java", "Jira", "Kayako", "Kerberos", "Kubernetes", "LDAP", "Lambda", "Library", "LinkedIn", "Linux", "Lists", "MDM", "MFA", "Mail", "Mailbox", "Mailchimp", "Malware", "Microsoft", "Monday.com", "MySQL", "NAS", "NetFlow", "Notification", "Notion", "Okta", "OneDrive", "OpenAI", "Organizer", "Outlook", "PDF", "PHP", "POP3", "Planner", "Playbook", "Plugin", "Plugins", "Portal", "Portals", "PowerShell", "Pro", "Project", "Pub/Sub", "QA", "QuickBooks", "Quiz", "RADIUS", "RDP", "RDS", "Ransomware", "Registry", "Repository", "S3", "SIEM", "SMS", "SMTP", "SQL", "SSH", "SSO", "SaaS", "Safari", "Salesforce", "Sandbox", "SaneArchive", "SaneBlackHole", "SaneCC", "SaneLater", "Scanner", "Scheduler", "Scripts", "Self-Hosted", "ServiceNow", "SharePoint", "Sheets", "Shopify", "Siri", "Slack", "Slides", "Software", "Spiceworks", "Splunk", "Spreadsheet", "Sudo", "Suite", "Superhuman", "TOTP", "Tableau", "Teams", "Terminal", "Terraform", "Ticketing", "Tracker", "Trello", "VPC", "VPN", "VPNs", "Vault", "Vaults", "VoIP", "WHOIS", "Watchtower", "WebSocket", "Webhook", "Webhooks", "WhatsApp", "Wiki", "Windows", "WordPress", "Workspace", "Yammer", "Zapier", "Zendesk", "Zoho", "Zoom", "analytics", "app", "chatbots", "iCloud", "iOS", "plugin", "plugins", "podcast", "syslog", "ticketing", "webhook", "wiki"]
 

 
# Build Aho-Corasick automaton
def build_automaton():
    automaton = ahocorasick.Automaton()
    for kw in actions:
        automaton.add_word(kw.lower(), ("action", kw))
    for kw in applications:
        automaton.add_word(kw.lower(), ("application", kw))
    for kw in objects:
        automaton.add_word(kw.lower(), ("object", kw))
    automaton.make_automaton()
    return automaton
 
# Classify ticket based on keywords
def classify(text, automaton):
    text = text.lower()
    found = set()
    for _, (typ, _) in automaton.iter(text):
        found.add(typ)
    return "ITO" if {"action", "application"}.issubset(found) else "Non-ITO"
 
# API to handle file upload and return zip
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

    # Split into two DataFrames
    ito_df = df[df['Category'] == 'ITO']
    non_ito_df = df[df['Category'] == 'Non-ITO']
    

    ito_df.to_csv('regex_ito_tickets.csv',index=False)
    non_ito_df.to_csv('regex_non_ito_tickets.csv', index = False)

    
    
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)





















