"""Streamlit Web UI for TestCase-Genie."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure src/ is on Python search path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
from dotenv import load_dotenv

from testcase_genie import __version__
from testcase_genie.agent import (
    EmptyInputError,
    GeminiAgent,
    GeminiRateLimitError,
    GeminiServiceError,
    JSONParsingError,
    MissingAPIKeyError,
)
from testcase_genie.exporter import suite_to_csv, suite_to_json, suite_to_markdown
from testcase_genie.generator import TestCaseGenerator
from testcase_genie.models import FrameworkType, GenerationConfig, TestCaseSuite

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="TestCase-Genie | AI Test Case & Automation Generator",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #1E88E5;
    }
    .badge-positive {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-negative {
        background-color: #ffebee;
        color: #c62828;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-edge {
        background-color: #fff8e1;
        color: #f57f17;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SAMPLE_STORIES = {
    "None": "",
    "🛒 E-Commerce Checkout": (
        "As a registered shopper on an e-commerce platform, I want to proceed from my cart "
        "to a single-page checkout, enter or select a shipping address, choose between Credit Card "
        "or PayPal payment methods, apply an optional promotional discount code, and place my order, "
        "so that I receive an instant on-screen order confirmation and an email receipt."
    ),
    "🔐 User Auth & MFA": (
        "As an enterprise employee, I want to log into the corporate dashboard using my corporate email "
        "and password, and if two-factor authentication (MFA) is enabled, enter a 6-digit Time-based One-Time "
        "Password (TOTP) from my authenticator app, with account lockout after 5 consecutive failed attempts "
        "within 15 minutes, so that company data remains secure against unauthorized access."
    ),
    "💳 Banking Fund Transfer": (
        "As a retail banking customer, I want to transfer money between my eligible savings and checking accounts "
        "or to an external beneficiary using an IBAN/account number, with instant balance validation, daily transfer limit "
        "enforcement ($5,000/day max), idempotency protection against double-clicking submit, and immediate debit "
        "reflection in my transaction ledger."
    ),
}

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Framework selection
    framework_choice = st.selectbox(
        "Automation Framework",
        options=[FrameworkType.PLAYWRIGHT.value, FrameworkType.SELENIUM.value],
        index=0,
        help="Select target framework for the generated Page Object Model automation code.",
    )
    
    # Test case count
    test_count = st.slider(
        "Number of Test Cases",
        min_value=3,
        max_value=15,
        value=5,
        step=1,
        help="Target number of test cases to produce across positive, negative, and edge scenarios.",
    )
    
    # Domain hint
    app_type = st.selectbox(
        "Application Domain",
        options=[
            "General Web/API",
            "E-Commerce & Retail",
            "Authentication & Security",
            "Banking & FinTech",
            "Healthcare & HIPAA",
            "SaaS & B2B Dashboard",
        ],
        index=0,
    )
    
    # Model configuration
    model_choice = st.text_input(
        "Gemini Model",
        value=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        help="Configurable via GEMINI_MODEL in .env or override here.",
    )

    st.markdown("---")
    st.markdown("### 🔑 API Key Status")
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    if has_api_key:
        st.success("✓ GEMINI_API_KEY detected")
    else:
        st.warning("⚠️ GEMINI_API_KEY not found in .env")
        custom_key = st.text_input("Enter Gemini API Key (Temporary)", type="password")
        if custom_key:
            os.environ["GEMINI_API_KEY"] = custom_key
            st.rerun()

    st.markdown("---")
    st.markdown(f"**TestCase-Genie v{__version__}**")
    st.caption("Powered by Google GenAI SDK & Page Object Model")

# --- Main App Header ---
st.markdown('<div class="main-header">🧞 TestCase-Genie</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Powered QA Test Case & Automation Code Generator for Senior QA Teams</div>',
    unsafe_allow_html=True,
)

# --- Sample Story Selector ---
col_sample, _ = st.columns([2, 1])
with col_sample:
    selected_sample = st.selectbox(
        "💡 Load a sample user story:",
        options=list(SAMPLE_STORIES.keys()),
        index=0,
    )

# --- Input Area (Tabs: Text vs File Upload) ---
input_tab1, input_tab2 = st.tabs(["✍️ Write / Paste User Story", "📂 Upload File (.txt, .md)"])

user_story_input = ""
with input_tab1:
    default_text = SAMPLE_STORIES.get(selected_sample, "")
    user_story_input = st.text_area(
        "User Story or Feature Specification:",
        value=default_text,
        height=140,
        placeholder="e.g. As a user, I want to reset my password using an email link with a 15-minute token expiry...",
    )

with input_tab2:
    uploaded_file = st.file_uploader("Upload user story or acceptance criteria file", type=["txt", "md"])
    if uploaded_file is not None:
        user_story_input = uploaded_file.read().decode("utf-8")
        st.info(f"Loaded {len(user_story_input)} characters from {uploaded_file.name}")

generate_btn = st.button("🚀 Generate Test Cases & Automation Code", type="primary", use_container_width=True)

# Session state initialization for caching generated suite
if "current_suite" not in st.session_state:
    st.session_state.current_suite = None

if generate_btn:
    if not user_story_input or not user_story_input.strip():
        st.error("Please provide a user story or upload a file before generating.")
    else:
        cfg = GenerationConfig(
            framework=FrameworkType(framework_choice),
            test_count=test_count,
            app_type=app_type if app_type != "General Web/API" else None,
        )

        with st.spinner("🤖 Consulting Gemini with QA Architect persona & generating Page Object Model code..."):
            try:
                agent = GeminiAgent(model=model_choice)
                generator = TestCaseGenerator(agent=agent)
                suite = generator.generate(user_story=user_story_input, config=cfg)
                st.session_state.current_suite = suite
                st.success(f"✓ Generated {len(suite.test_cases)} scenarios and POM starter code successfully!")
            except MissingAPIKeyError as e:
                st.error(f"🔑 Missing API Key: {e}")
                st.info("Add GEMINI_API_KEY to your local `.env` file or provide it in the sidebar.")
            except EmptyInputError as e:
                st.error(f"Input Error: {e}")
            except GeminiRateLimitError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}. Please wait a moment and retry.")
            except (GeminiServiceError, JSONParsingError) as e:
                st.error(f"Generation Error: {e}")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")

# --- Render Results ---
current_suite: TestCaseSuite = st.session_state.current_suite
if current_suite:
    st.markdown("---")
    st.subheader(f"📋 {current_suite.title}")
    if current_suite.description:
        st.caption(f"**Requirement:** {current_suite.description}")

    # Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    total_cases = len(current_suite.test_cases)
    pos_cases = sum(1 for tc in current_suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "positive")
    neg_cases = sum(1 for tc in current_suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "negative")
    edge_cases = sum(1 for tc in current_suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "edge")

    with m_col1:
        st.metric("Total Scenarios", total_cases)
    with m_col2:
        st.metric("Positive (Happy Path)", pos_cases)
    with m_col3:
        st.metric("Negative (Error Paths)", neg_cases)
    with m_col4:
        st.metric("Edge & Boundary Cases", edge_cases)

    # View Tabs: Structured Cards, Table View, Code View, Export
    tab_cards, tab_table, tab_code, tab_export = st.tabs([
        "🃏 Test Case Details",
        "📊 Summary Table",
        "💻 Automation Code (POM)",
        "💾 Download & Export",
    ])

    with tab_cards:
        for tc in current_suite.test_cases:
            t_val = tc.type.value if hasattr(tc.type, "value") else str(tc.type)
            p_val = tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)

            type_badge = (
                f'<span class="badge-positive">POSITIVE</span>'
                if t_val == "positive"
                else (f'<span class="badge-negative">NEGATIVE</span>' if t_val == "negative" else f'<span class="badge-edge">EDGE</span>')
            )

            header_label = f"{tc.id}: {tc.title} ({t_val.upper()} | Priority: {p_val.upper()})"
            with st.expander(header_label, expanded=True):
                st.markdown(f"**Type:** {type_badge} &nbsp;&nbsp; | &nbsp;&nbsp; **Priority:** `{p_val.upper()}`", unsafe_allow_html=True)
                
                st.markdown("**Preconditions:**")
                if tc.preconditions:
                    for pre in tc.preconditions:
                        st.markdown(f"- {pre}")
                else:
                    st.markdown("- *None specified*")

                st.markdown("**Execution Steps:**")
                for idx, step in enumerate(tc.steps, 1):
                    st.markdown(f"{idx}. {step}")

                st.markdown("**Expected Outcome:**")
                st.info(tc.expected_result)

    with tab_table:
        table_data = []
        for tc in current_suite.test_cases:
            table_data.append({
                "ID": tc.id,
                "Title": tc.title,
                "Type": (tc.type.value if hasattr(tc.type, "value") else str(tc.type)).upper(),
                "Priority": (tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)).upper(),
                "Steps": " | ".join(tc.steps),
                "Expected Result": tc.expected_result,
            })
        st.dataframe(table_data, use_container_width=True)

    with tab_code:
        if current_suite.generated_code:
            fw_label = current_suite.framework.value if current_suite.framework else "python"
            st.markdown(f"**Starter Automation Code ({fw_label.upper()} - Page Object Model):**")
            st.code(current_suite.generated_code, language="python")
        else:
            st.info("No automation code generated yet.")

    with tab_export:
        st.markdown("### 📥 Download Generated Assets")
        json_str = suite_to_json(current_suite)
        md_str = suite_to_markdown(current_suite)
        csv_str = suite_to_csv(current_suite)

        exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)
        with exp_col1:
            st.download_button(
                label="📄 Download Markdown (.md)",
                data=md_str,
                file_name=f"{current_suite.title.lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with exp_col2:
            st.download_button(
                label="🧾 Download JSON (.json)",
                data=json_str,
                file_name=f"{current_suite.title.lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True,
            )
        with exp_col3:
            st.download_button(
                label="📊 Download CSV (.csv)",
                data=csv_str,
                file_name=f"{current_suite.title.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with exp_col4:
            if current_suite.generated_code:
                st.download_button(
                    label="🐍 Download Python Code (.py)",
                    data=current_suite.generated_code,
                    file_name=f"test_{current_suite.title.lower().replace(' ', '_')}.py",
                    mime="text/x-python",
                    use_container_width=True,
                )
