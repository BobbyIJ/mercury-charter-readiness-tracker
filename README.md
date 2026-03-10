# 🏦 Mercury Charter Readiness Tracker: AI-Powered Compliance Pipeline

An automated, LLM-driven data pipeline designed to cross-reference internal draft policies against federal regulatory mandates, identifying compliance gaps and pushing them directly to Linear.

**Built as a Proof of Concept (PoC) for Mercury.**

---

## 🎯 Strategic Rationale
As Mercury recently submitted an application for a national bank charter to the Office of the Comptroller of the Currency (OCC), there is a strong need for alignment of the company's policies with the federal government's requirements pertaining to BSA / AML Compliance, Liquidity & FUnds Management, Information Security, and Capital Adequacy amongst other areas. Despite this need, federal government documents comprise thousands of pages across different manuals, websites, and other reference sources which makes cross-referencing a highly manual process with a propensity for errors.

This system was designed to solve that bottleneck by transforming static government PDFs into structured JSON and pushing compliance gaps directly into the tools where Mercury employees already engage (Linear). This makes compliance an agile and continuous process rather than a black box expending valuable employee time.

## 🏗️ Architecture & Tech Stack
This tool bridges the gap between legal & compliance frameworks and engineering execution using a modular Python backend.

* **Frontend UI:** Streamlit (Custom CSS for native light/dark mode and SaaS aesthetics)
* **LLM / Parsing Engine:** Google GenAI SDK (Gemini 2.5 Flash for high-speed, 1M+ token context ingestion)
* **Internal Data Pipeline:** Notion API (Recursive block extraction)
* **Ticketing & Action:** Linear GraphQL API

## ✨ Core Workflows
1. **Enterprise Knowledge Ingestion:** Securely connects to an internal Notion workspace, recursively diving into sub-pages to extract the plain-text of current draft policies.
2. **Regulatory Mandate Extraction:** Ingests dense federal regulatory PDFs. Utilizing a massive context window, it extracts distinct, quantitative compliance mandates and structures them into a strict JSON schema.
3. **Evaluation Engine:** Cross-references the internal policy text against the structured federal mandates to identify gaps, missing thresholds, or non-compliant internal targets.
4. **Automated Ticketing:** Formats detected gaps into detailed bug reports and pushes them directly into an active Linear workspace via GraphQL mutations.

---

## 🚧 Current Limitations & Scalability Roadmap
As a v1 Proof of Concept, this architecture makes several deliberate scoping tradeoffs to prioritize speed and core functionality. A production-grade deployment would require the following expansions:

* **Single-Document Scope:** The current extraction pipeline is hardcoded to evaluate the OCC Liquidity Handbook. It needs an orchestration layer to dynamically route and evaluate multiple manuals (e.g., FFIEC BSA/AML, FDIC guidelines, OCC Licensing Manual, etc.) simultaneously.
* **Notion Ingestion Boundaries:** The Notion API integration successfully parses recursive child pages and text blocks, but it does not currently follow or scrape external web URLs, nor does it parse complex embedded databases. 
* **API Token Constraints:** To prevent output truncation errors during JSON generation, the prompt explicitly limits the LLM to outputting the top 10 compliance gaps since it uses free Gemini API. Production scaling would require a more exhaustive generation of policies.
* **Static Ticket Routing:** The Linear GraphQL mutation currently assigns all compliance blockers to a single default team. A mature version would parse the "domain" of the gap (e.g., InfoSec vs. Capital Adequacy) and route the ticket to the specific responsible team.

---

## 🚀 Local Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/mercury-charter-readiness.git](https://github.com/yourusername/mercury-charter-readiness.git)
cd mercury-charter-readiness

### 2. Set up the virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

### 3. Create a .env file in the root directory and add your secure API keys:
NOTION_TOKEN="ntn_your_notion_internal_integration_token"
NOTION_POLICY_PAGE_ID="your_target_page_id"
GEMINI_API_KEY="AIzaSy_your_google_ai_studio_key"
LINEAR_API_KEY="lin_api_your_personal_api_key"

### 4. Run the application
```bash
python -m streamlit run dashboard.py