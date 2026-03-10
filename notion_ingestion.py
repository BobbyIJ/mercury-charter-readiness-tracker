import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
POLICY_PAGE_ID = os.getenv("NOTION_POLICY_PAGE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_policy_text(page_id, depth=0):
    """
    Connects to the Notion API, retrieves text blocks, and recursively 
    dives into sub-pages to extract nested policy documents.
    """
    if not page_id or not NOTION_TOKEN:
        print("Error: Missing Notion API Token or Page ID.")
        return ""

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching Notion data: {response.status_code}")
        return ""

    blocks = response.json().get("results", [])
    full_policy_text = ""
    indent = "  " * depth # For clean formatting if we go deep

    for block in blocks:
        block_type = block.get("type")
        
        # 1. Extract Standard Text Blocks
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
            rich_text_array = block.get(block_type, {}).get("rich_text", [])
            for text_obj in rich_text_array:
                full_policy_text += text_obj.get("plain_text", "")
            full_policy_text += "\n"
            
        # 2. The Magic: Recursively dive into Sub-Pages
        elif block_type == "child_page":
            child_title = block.get("child_page", {}).get("title", "Untitled Sub-Page")
            child_id = block.get("id")
            
            full_policy_text += f"\n{indent}--- BEGIN SUB-POLICY: {child_title} ---\n"
            # The function calls itself with the new child ID
            full_policy_text += fetch_notion_policy_text(child_id, depth + 1)
            full_policy_text += f"{indent}--- END SUB-POLICY: {child_title} ---\n\n"

    return full_policy_text

# --- Execution & Testing ---
if __name__ == "__main__":
    print("Authenticating and traversing Notion workspace...")
    policy_text = fetch_notion_policy_text(POLICY_PAGE_ID)
    
    if policy_text.strip():
        print("\n✅ Extraction Successful! Here is the compiled policy text:\n")
        print(policy_text)
    else:
        print("\n❌ Extraction returned empty text. Ensure there is actual text inside the pages, not just links.")