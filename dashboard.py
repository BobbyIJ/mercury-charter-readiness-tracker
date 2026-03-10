import streamlit as st
import json
import os
from dotenv import load_dotenv

from notion_ingestion import fetch_notion_policy_text
from occ_extraction import extract_regulatory_rules
from evaluation_engine import evaluate_compliance_gaps, push_to_linear

load_dotenv()
POLICY_PAGE_ID = os.getenv("NOTION_POLICY_PAGE_ID")
PDF_FILENAME = "OCC Handbook - Liquidity.pdf"

# --- UI Configuration ---
st.set_page_config(page_title="Mercury Charter Readiness", layout="wide")

# --- Custom Mercury/Notion CSS ---
st.markdown("""
    <style>
    /* Hide default Streamlit chrome for a cleaner app-like feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dynamic Theme Variables */
    :root {
        --card-bg: #ffffff;
        --card-border: #eaeaea;
        --text-main: #111111;
        --text-muted: #666666;
        --accent: #000000;
        --shadow: rgba(0, 0, 0, 0.04);
    }

    /* Dark Mode Overrides */
    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg: #111111;
            --card-border: #2a2a2a;
            --text-main: #f2f2f2;
            --text-muted: #888888;
            --accent: #ffffff;
            --shadow: rgba(0, 0, 0, 0.2);
        }
    }

    /* Minimalist Ticket Cards */
    .ticket-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px var(--shadow);
        transition: all 0.2s ease-in-out;
    }
    
    .ticket-card:hover {
        border-color: var(--text-muted);
    }

    .ticket-badge {
        font-family: monospace;
        font-size: 0.8rem;
        background-color: var(--card-border);
        color: var(--text-main);
        padding: 4px 8px;
        border-radius: 4px;
        margin-bottom: 12px;
        display: inline-block;
    }

    .ticket-title {
        color: var(--text-main);
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .ticket-desc {
        color: var(--text-muted);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Clean up headers */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'policy_text' not in st.session_state:
    st.session_state['policy_text'] = None
if 'occ_rules' not in st.session_state:
    st.session_state['occ_rules'] = None
if 'gaps' not in st.session_state:
    st.session_state['gaps'] = None

# --- Sidebar: Data Controls ---
with st.sidebar:
    st.markdown("### Architecture")
    st.caption("Draft internal policies parsed from Notion via API. Regulatory rules extracted from 100-page OCC Liquidity Handbook PDF using Gemini 2.5 Flash. Gaps pushed to Linear via GraphQL.")
    st.divider()
    
    st.markdown("#### 1. Internal Policy")
    if st.button("Sync Notion Workspace", use_container_width=True):
        with st.spinner("Fetching..."):
            policy = fetch_notion_policy_text(POLICY_PAGE_ID)
            if policy:
                st.session_state['policy_text'] = policy
                st.success("Synced")

    st.markdown("#### 2. Regulatory Mandates")
    if st.button("Parse OCC Handbook", use_container_width=True):
        with st.spinner("Analyzing..."):
            rules = extract_regulatory_rules(PDF_FILENAME)
            if rules:
                st.session_state['occ_rules'] = rules
                st.success("Extracted")

# --- Main Workspace ---
st.title("Mercury Charter Readiness Tracker")
st.markdown("Automated OCC compliance evaluation system mapping draft internal policies against federal mandates.")
st.write("") # Whitespace

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Internal Policy", value="Loaded" if st.session_state['policy_text'] else "Pending")
with col2:
    st.metric(label="Extracted Mandates", value=len(st.session_state['occ_rules']) if st.session_state['occ_rules'] else 0)
with col3:
    st.metric(label="Compliance Gaps", value=len(st.session_state['gaps']) if st.session_state['gaps'] else 0)

st.divider()

# --- Evaluation Engine ---
col_action, col_empty = st.columns([1, 2])
with col_action:
    if st.button("Run Evaluation Engine", type="primary", use_container_width=True):
        if not st.session_state['policy_text'] or not st.session_state['occ_rules']:
            st.error("Please sync Notion and parse the OCC Handbook first.")
        else:
            with st.spinner("Evaluating compliance gaps & pushing to Linear..."):
                gaps = evaluate_compliance_gaps(st.session_state['policy_text'], st.session_state['occ_rules'])
                st.session_state['gaps'] = gaps
                if gaps:
                    push_to_linear(gaps)

st.write("") # Whitespace

# --- Display Results ---
if st.session_state['gaps']:
    st.markdown("### Identified Compliance Gaps for Mercury Charter")
    
    for gap in st.session_state['gaps']:
        st.markdown(f"""
            <div class="ticket-card">
                <div class="ticket-badge">{gap.get('requirement_id', 'ID')}</div>
                <div class="ticket-title">{gap.get('title', 'Untitled')}</div>
                <div class="ticket-desc">{gap.get('description', 'No description.')}</div>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state['gaps'] == []:
    st.success("No gaps found. Policy is fully compliant.")