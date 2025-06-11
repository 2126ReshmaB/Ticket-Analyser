import os
import json
from typing import Tuple, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from keywords_list import get_keywords

class KeywordClassifier:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_version="2024-02-01",
            azure_deployment="gpt-4o",
            azure_endpoint="https://mavericks-secureapi.azurewebsites.net/api/azureai",
            api_key="fc3498dfabef692d",
            temperature=0.3,
            max_tokens=2000
        )
        self.batch_size = 50

    def classify_keywords(self, keyword_list: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """Classify keywords into actions, applications, and objects."""
        actions = set()
        applications = set()
        objects = set()

        for i in range(0, len(keyword_list), self.batch_size):
            batch = keyword_list[i:i + self.batch_size]
            
            messages = [
                SystemMessage(content="""
Classify the following IT-related keywords into exactly three categories:

1. actions — verbs representing operations (e.g., 'install', 'restart', 'configure')
2. applications — names of software, tools, or systems (e.g., 'Outlook', 'SAP', 'Citrix')
3. objects — hardware or infrastructure components (e.g., 'printer', 'server', 'router')

Return a JSON object with exactly these keys: 'actions', 'applications', 'objects'.
Exclude any keywords that are unclear, irrelevant, or do not fit any category.
"""),
                HumanMessage(content=f"Keywords: {json.dumps(batch)}")
            ]

            try:
                response = self.llm.invoke(
                    messages,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.content)
                actions.update(result.get("actions", []))
                applications.update(result.get("applications", []))
                objects.update(result.get("objects", []))
            except Exception:
                continue

        return sorted(actions), sorted(applications), sorted(objects)

def get_keywords_from_llm():


    classifier = KeywordClassifier()
    keywords = get_keywords()
    actions, applications, objects = classifier.classify_keywords(keywords)
    return actions, applications, objects
