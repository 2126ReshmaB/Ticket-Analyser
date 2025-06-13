import pandas as pd
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from tqdm import tqdm



def llm_classification():
    print("-----------------------------------------")
    def setup_llm():
        return AzureChatOpenAI(
        openai_api_key="11c02d84ed6f75e5",
        openai_api_version="2024-02-01",
        deployment_name="gpt-4o",
        azure_endpoint="https://mavericks-secureapi.azurewebsites.net/api/azureai",
        temperature=0.2
    )

    def classify_ticket(llm, description):
        if not description or str(description).strip() == "":
            return "Empty"

        messages = [
        SystemMessage(
            content="You classify tickets as either 'Non-ITO' (valid business requests) "
                   "or 'Rubbish' (spam/tests/invalid). Only respond with those exact terms."
        ),
        HumanMessage(content=f"Ticket: {description}")
    ]
    
        try:
            response = llm(messages)
            return response.content.strip() if response.content.strip() in ["Non-ITO", "Rubbish"] else "Invalid"
        except:
            return "Error"

    def process_tickets(input_file, output_file):
        llm = setup_llm()
        tickets = pd.read_csv(input_file)
    
        if "Description" not in tickets.columns:
            print("Missing 'Document' column in input file")
            return
    
        results = []
        for _, row in tqdm(tickets.iterrows(), total=len(tickets)):
            classification = classify_ticket(llm, row["Description"])
            results.append(classification)
    
        tickets["LLM_Classification"] = results
        tickets.to_csv(output_file, index=False)
    
        print("\nClassification Results:")
        print(tickets["LLM_Classification"].value_counts())
        print("\nDone!")

    if __name__ == "__main__":
        process_tickets(
        input_file="non_ito_predictions.csv",
        output_file="classified_tickets.csv"
    )