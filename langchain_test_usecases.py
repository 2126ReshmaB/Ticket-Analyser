import os
import json
from typing import Tuple, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from keywords_list import get_keywords

import os
import json
from typing import Tuple, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
 
class KeywordClassifier:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_version="2024-02-01",
            azure_deployment="gpt-4o",
            azure_endpoint="https://mavericks-secureapi.azurewebsites.net/api/azureai",
            api_key="11c02d84ed6f75e5",
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
                SystemMessage(content="""Classify IT keywords into exactly 3 categories:
                1. actions (verbs like 'install', 'restart')
                2. applications (software like 'Outlook', 'SAP')
                3. objects (hardware/components like 'printer', 'server')
                
                Return ONLY a JSON object with these three keys. Omit unclear or irrelevant words."""),
 
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
                continue  # You can log or handle errors if needed
 
        return sorted(actions), sorted(applications), sorted(objects)
 

def get_keywords_from_llm():


    classifier = KeywordClassifier()
    keywords = get_keywords()
    actions, applications, objects = classifier.classify_keywords(keywords)
    print(applications)

get_keywords_from_llm()
