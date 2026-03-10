import os
import json
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import our custom pipelines
from notion_ingestion import fetch_notion_policy_text
from occ_extraction import extract_regulatory_rules

# 1. Load Credentials
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
POLICY_PAGE_ID = os.getenv("NOTION_POLICY_PAGE_ID")

client = genai.Client(api_key=GEMINI_API_KEY)
PDF_FILENAME = "OCC Handbook - Liquidity.pdf"

def evaluate_compliance_gaps(policy_text, regulatory_rules):
    """Uses Gemini to compare internal policy against external rules to find gaps."""
    print("\n🧠 Evaluating compliance gaps using Gemini 2.5 Flash...")
    
    system_prompt = f"""
    You are an expert Chief Compliance Officer. Compare the Internal Company Policy against the Required Regulatory Mandates.
    Identify which regulatory mandates are NOT fully met or addressed by the internal policy.
    
    Internal Company Policy:
    {policy_text}
    
    Required Regulatory Mandates:
    {json.dumps(regulatory_rules)}
    
    Output a JSON array of gaps. Each object must have:
    - "requirement_id": The ID of the failed rule.
    - "title": A short, 4-5 word title for the ticket.
    - "description": A brief explanation of what is missing from the policy and what needs to be added.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    return json.loads(response.text)

def push_to_linear(gaps):
    """Creates actionable tickets in Linear for each compliance gap."""
    if not gaps:
        print("🎉 No compliance gaps found! Policy is fully compliant.")
        return

    print(f"\n🚀 Pushing {len(gaps)} compliance blocker(s) to Linear...")
    
    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }

    # First, we must fetch your Linear Team ID (Linear requires this to create an issue)
    team_query = {"query": "{ teams { nodes { id name } } }"}
    team_res = requests.post("https://api.linear.app/graphql", headers=headers, json=team_query)
    
    try:
        team_id = team_res.json()['data']['teams']['nodes'][0]['id']
    except (KeyError, IndexError):
        print("❌ Could not fetch Linear Team ID. Check your LINEAR_API_KEY.")
        return

    # Loop through each gap and create a ticket
    for gap in gaps:
        mutation = """
        mutation IssueCreate($title: String!, $description: String!, $teamId: String!) {
          issueCreate(input: {
            title: $title,
            description: $description,
            teamId: $teamId
          }) {
            success
            issue {
              identifier
              url
            }
          }
        }
        """
        
        variables = {
            "title": f"[Compliance Blocker] {gap['requirement_id']}: {gap['title']}",
            "description": gap['description'],
            "teamId": team_id
        }

        issue_res = requests.post(
            "https://api.linear.app/graphql", 
            headers=headers, 
            json={"query": mutation, "variables": variables}
        )
        
        result = issue_res.json()
        if result.get('data', {}).get('issueCreate', {}).get('success'):
            issue_url = result['data']['issueCreate']['issue']['url']
            print(f"✅ Ticket Created: {issue_url}")
        else:
            print(f"⚠️ Failed to create ticket for {gap['requirement_id']}: {result}")

# --- Execution ---
if __name__ == "__main__":
    print("=== STARTING COMPLIANCE EVALUATION PIPELINE ===")
    
    # Step 1: Ingest Internal Policy
    print("\n📥 Step 1: Fetching internal policy from Notion...")
    notion_policy = fetch_notion_policy_text(POLICY_PAGE_ID)
    
    if not notion_policy.strip():
        print("❌ Failed to load Notion policy. Aborting.")
        exit()

    # Step 2: Ingest Regulatory JSON
    print("\n📥 Step 2: Extracting rules from OCC PDF...")
    occ_rules = extract_regulatory_rules(PDF_FILENAME)
    
    if not occ_rules:
        print("❌ Failed to parse OCC rules. Aborting.")
        exit()

    # Step 3: Evaluate Gaps
    print("\n🔍 Step 3: Cross-referencing documents...")
    compliance_gaps = evaluate_compliance_gaps(notion_policy, occ_rules)

    # Step 4: Push to Linear
    print("\n🎫 Step 4: Generating Engineering Tickets...")
    push_to_linear(compliance_gaps)
    
    print("\n=== PIPELINE COMPLETE ===")