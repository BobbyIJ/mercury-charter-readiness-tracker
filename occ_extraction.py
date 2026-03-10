import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load credentials
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit()

# 2. Configure the new Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Define the PDF file name
PDF_FILENAME = "OCC Handbook - Liquidity.pdf" 

def extract_regulatory_rules(pdf_path):
    print(f"Uploading '{pdf_path}' to Gemini's secure environment...")
    
    try:
        # Upload the file
        uploaded_file = client.files.upload(file=pdf_path)
        
        # Give Google's servers time to process the 100-page PDF
        print("Upload complete. Processing file on server (waiting 15 seconds)...")
        time.sleep(15) 
        
        print("Analyzing document...")
        system_prompt = """
        You are an expert regulatory compliance architect and banking examiner. Read the provided banking regulatory manual and extract the 10 most critical and distinct quantitative compliance mandates for testing purposes.
        
        Output a JSON array of objects. Do not include markdown formatting.
        Each object must have exactly these keys:
        - "requirement_id": A unique sequential string (e.g., "OCC-LIQ-001").
        - "domain": Categorize as "BSA/AML", "Liquidity", "Information Security", or "Capital Adequacy".
        - "rule_summary": A concise, 1-sentence summary of the rule.
        - "specific_threshold": The exact quantitative metric, frequency, or technical standard. If none, output "Qualitative".
        - "regulatory_source": The name of the document.
        """

        # Generate content using the modern Gemini 2.5 Pro model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, uploaded_file],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        # Clean up: delete the file from Google's servers after processing
        client.files.delete(name=uploaded_file.name)
        
        return json.loads(response.text)

    except FileNotFoundError:
        print(f"❌ Error: Could not find the file '{pdf_path}' in your workspace directory.")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

# --- Execution & Testing ---
if __name__ == "__main__":
    extracted_json = extract_regulatory_rules(PDF_FILENAME)
    
    if extracted_json:
        print("\n✅ Extraction Successful! Here is the structured JSON output:\n")
        print(json.dumps(extracted_json, indent=2))