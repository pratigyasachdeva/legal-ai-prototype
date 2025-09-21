import streamlit as st
import PyPDF2
import docx
import openai
import google.generativeai as genai
import re
import plotly.express as px
from collections import Counter


# ================================
# 🌟 Custom Branding & UI Styling
# ================================
st.set_page_config(
    page_title="Legal AI Prototype",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #f9fafc, #eaeef5);
        font-family: 'Segoe UI', sans-serif;
    }

    /* Title Card */
    .title-card {
        background: linear-gradient(90deg, #0a1a40, #1c2e70); /* darker navy */
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        margin-bottom: 25px;
    }
    .title-card h1 {
        font-size: 38px;
        margin: 0;
    }
    .title-card p {
        font-size: 16px;
        opacity: 0.9;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1c2e70, #32499c); /* darker */
        color: white;
        border-radius: 8px;
        padding: 8px 18px;
        border: none;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0f1d4d, #32499c);
        transform: scale(1.02);
    }

    /* Risk Labels */
    .risk-high {
        background-color: #ffcccc;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
        color: #b71c1c;
    }
    .risk-medium {
        background-color: #fff2cc;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
        color: #e65100;
    }
    .risk-low {
        background-color: #ccffcc;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
        color: #1b5e20;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 16px !important;
    }
    .streamlit-expander {
        border-radius: 10px !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #eeeeee;
        color: #0a1a40;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #0a1a40 !important;
    }
    section[data-testid="stSidebar"] .stButton>button {
        background: #1c2e70;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)


# ================================
# 🔹 Branding Header
# ================================
st.markdown("""
<div class="title-card">
    <h1>⚖️ Legal Document Simplifier</h1>
    <p>AI-powered legal document analysis, risk highlighting & clause simplification</p>
</div>
""", unsafe_allow_html=True)


# ================================
# 🔹 Backend Logic (Untouched)
# ================================
genai.configure(api_key="AIzaSyDx7gLntgYAqPFGMhdp0ZKbJLofWLhSeuU")

def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = file.getvalue().decode("utf-8")
    return text

def simplify_text(text):
    prompt = f"Explain this legal text in simple English:\n\n{text[:2000]}"
    model = genai.GenerativeModel("gemini-1.5-flash")  # fast & free model
    response = model.generate_content(prompt)
    return response.text



uploaded_file = st.file_uploader("📂 Upload a legal document (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    raw_text = extract_text(uploaded_file)

    # 1️⃣ Document Text Preview – Automatic
    st.subheader("📖 Document Text Preview")
    st.write(raw_text[:2000] + " ...")

    # 2️⃣ Simplified Summary – Button Trigger
    if st.button("✨ Simplify Document"):
        st.write("🚀 AI is simplifying the document...")
        simplified_text = simplify_text(raw_text)
        st.subheader("📜 Simplified Summary")
        st.write(simplified_text)

    # Sidebar Clause Explainer
    st.sidebar.subheader("🔎 Clause Explainer")
    clause_input = st.sidebar.text_area("Paste a clause to explain", height=150)

    if st.sidebar.button("Explain Clause"):
        if clause_input.strip() == "":
            st.sidebar.warning("⚠️ Please enter a clause first!")
        else:
            st.sidebar.write("AI is explaining your clause...")
            clause_explanation = simplify_text(clause_input)
            st.sidebar.subheader("Clause Explanation")
            st.sidebar.write(clause_explanation)

    # 4️⃣ AI-Powered Risk Highlighting – Inline + Highlighted (Upgraded)
    risk_keywords = [
        "termination", "arbitration", "liability", "penalty", "indemnity",
        "confidentiality", "governing law", "force majeure", "breach", 
        "warranty", "notice", "jurisdiction", "assignment", "non-compete"
    ]

    if st.button("Analyze Risk Clauses"):
        st.sidebar.success("⚠️ This document contains risk clauses")
        st.write("⚠️ AI is analyzing risk in your document...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        highlighted_text = raw_text

        i = 0
        for keyword in risk_keywords:
            sentences = [s.strip() for s in raw_text.split(".") if keyword.lower() in s.lower()]
            for sent in sentences:
                if not sent:
                    continue
                prompt = f"Evaluate risk level (low/medium/high) of this legal clause:\n\n{sent}"
                response = model.generate_content(prompt)
                risk_level = response.text.lower().strip()

                # Background color mapping for heatmap effect
                if "high" in risk_level:
                    bg_color = "#ffcccc"  # light red
                elif "medium" in risk_level:
                    bg_color = "#fff2cc"  # light yellow
                else:
                    bg_color = "#ccffcc"  # light green

                # Color mapping inside the loop, before using it
                if "high" in risk_level:
                    color = "red"
                elif "medium" in risk_level:
                    color = "orange"
                else:
                    color = "green"

                # Replace inline text with colored span
                highlighted_text = highlighted_text.replace(
                    sent,
                    f"<span style='color:black; background-color:{bg_color}; font-weight:bold'>{sent}</span>"
                )

                # Expandable card with clause + explanation toggle
                # Inside the existing expander where clause is shown
                with st.expander(f"{risk_level.capitalize()} Risk: {sent[:50]}...", expanded=False):
                    st.markdown(
                        f"<div style='background-color:{bg_color}; padding:10px; border-radius:5px'>"
                        f"<strong>{sent}</strong></div>",
                        unsafe_allow_html=True
                    )
                    
                    if st.button(f"Explain this clause {i}", key=f"explain_{i}"):
                        explanation = simplify_text(rc['text'])
                        st.write(explanation)

                    if st.button(f"Suggest Fair Terms {i}", key=f"redline_{i}"):
                        suggestion = model.generate_content(f"Suggest fair/legal improvements:\n{rc['text']}").text
                        st.markdown(f"<span style='color:green'>{suggestion}</span>", unsafe_allow_html=True)
                
                i += 1

        st.subheader("AI-Powered Risk Highlighted Document")
        st.markdown(highlighted_text, unsafe_allow_html=True)

    # 🔹 Phase 2: Visual Upgrades for Risk Highlighting

    if st.button("Show Visual Risk Insights"):
        st.write("📊 Generating visual insights for the document...")

        risk_keywords = ["termination", "arbitration", "liability", "penalty", "indemnity",
                        "confidentiality", "governing law", "force majeure", "breach", 
                        "warranty", "notice", "jurisdiction", "assignment", "non-compete"]

        model = genai.GenerativeModel("gemini-1.5-flash")
        risk_clauses = []

        # Collect clauses with risk level
        for keyword in risk_keywords:
            sentences = [s for s in raw_text.split(".") if keyword.lower() in s.lower()]
            for sent in sentences:
                prompt = f"Evaluate risk level (low/medium/high) of this legal clause:\n\n{sent}"
                response = model.generate_content(prompt)
                risk_level = response.text.lower().strip()
                risk_clauses.append({
                    "text": sent.strip(),
                    "level": risk_level
                })

        # ----- Executive Summary (Top 5 Points) -----
        st.subheader("📝 Executive Summary (Top 5 Risk Points)")
        top5 = risk_clauses[:5] if len(risk_clauses) >= 5 else risk_clauses
        for i, rc in enumerate(top5):
            st.markdown(f"{i+1}. **{rc['level'].capitalize()} Risk:** {rc['text'][:120]}...")

        # ----- Risk Heatmap / Clause Cards -----
        st.subheader("🔥 Clause Heatmap & Expandable Cards")
        for i, rc in enumerate(risk_clauses):
            color = "#ffcccc" if "high" in rc["level"] else ("orange" if "medium" in rc["level"] else "green")
            with st.expander(f"{rc['level'].capitalize()} Risk: {rc['text'][:50]}...", expanded=False):
                # Clause text with heatmap highlight
                st.markdown(f"<span style='background-color:{color}; padding:2px'>{rc['text']}</span>", unsafe_allow_html=True)
                
                # Toggle button for AI explanation
                if st.button(f"Explain this clause", key=f"explain_{i}"):
                    explanation = simplify_text(rc['text'])
                    st.write(explanation)
                
                # One-Click Redline Suggestion
                if st.button(f"Suggest Fair Terms", key=f"redline_{i}"):
                    prompt = f"Suggest fair/legal improvements for this clause:\n\n{rc['text']}"
                    suggestion = model.generate_content(prompt).text
                    st.markdown(f"<span style='color:green'>{suggestion}</span>", unsafe_allow_html=True)

        # ----- Risk Score Pie Chart -----
        st.subheader("📊 Overall Risk Distribution")

        # Collect risk levels from risk_clauses
        levels = [rc["level"] for rc in risk_clauses]

        # Count occurrences of each level (high, medium, low)
        level_counts = Counter(levels)

        # Ensure all 3 levels are represented, even if their count is 0
        for lvl in ["high", "medium", "low"]:
            if lvl not in level_counts:
                level_counts[lvl] = 0

        # Create a Pie Chart
        fig = px.pie(
            names=list(level_counts.keys()),  # Names for the sections
            values=list(level_counts.values()),  # The count of each risk level
            color=list(level_counts.keys()),  # Color by risk level
            color_discrete_map={"high": "red", "medium": "orange", "low": "green"},
            title="📊 Overall Risk Distribution",  # Title
            labels={"high": "High Risk", "medium": "Medium Risk", "low": "Low Risk"}  # Custom labels
        )

        # Adjust the appearance for better clarity
        fig.update_traces(textinfo="percent+label", pull=[0.1, 0.1, 0.1])  # Show percentage + label, with slight pull on each slice

        # Display the Pie chart
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(" Keywords")

        tooltips = {
            "Indemnity": "Protection against loss or damage",
            "Arbitration": "Legal dispute resolved outside court",
            "Liability": "Legal responsibility for damages",
            "Confidentiality": "Obligation to keep information secret",
            "Force Majeure": "Unforeseeable circumstances that prevent contract fulfillment",
            "Breach": "Failure to fulfill contractual obligations",
            "Warranty": "A guarantee about the quality or performance of something",
            "Notice": "Formal written notification",
            "Jurisdiction": "The legal authority over a particular area or case",
            "Assignment": "Transfer of rights or obligations",
            "Non-compete": "Clause preventing competition for a period"
        }

        # Show each keyword in an expander so user can click and see explanation
        for kw, desc in tooltips.items():
            with st.expander(f"{kw}"):
                st.write(desc)


# ===============================
# 💬 Floating Chatbot (One-Click Toggle)
# ===============================

# CSS
st.markdown("""
<style>
.chat-container {
    position: fixed;
    bottom: 25px;
    right: 25px;
    text-align: center;
    z-index: 9999;
}

.chat-button {
    width: 75px;
    height: 75px;
    background-color: #1a237e; 
    color: white; 
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.25);
    margin: auto;
    border: none;
}

.chat-label {
    font-size: 14px;
    color: #1a237e;
    margin-top: 6px;
    font-weight: 600;
}

.chat-window {
    position: fixed;
    bottom: 100px;
    right: 25px;
    width: 350px;
    max-height: 400px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    padding: 15px;
    overflow-y: auto;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)


# ===============================
# Initialize State
# ===============================
if "show_chat" not in st.session_state:
    st.session_state["show_chat"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# ===============================
# Sidebar Button + Label
# ===============================
with st.sidebar:
    st.markdown('<div style="text-align:center; margin-top:20px;">', unsafe_allow_html=True)

    if st.button("💬", key="chat_toggle_btn_sidebar"):
        st.session_state["show_chat"] = not st.session_state["show_chat"]

    st.markdown("<div style='color:#1a237e; font-weight:600; margin-top:6px;'>Ask Me!</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===============================
# Chat Window
# ===============================
if st.session_state["show_chat"]:
    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    st.subheader("Contract Q&A Assistant 🤖")

    # Show chat history
    for role, msg in st.session_state["chat_history"]:
        if role == "You":
            st.markdown(
                f"<div style='text-align:right; color:#1a237e;'><b>You:</b> {msg}</div>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='text-align:left; color:#000;'><b>AI:</b> {msg}</div>", 
                unsafe_allow_html=True
            )

    # User input
    user_input = st.chat_input("Ask about the contract...")
    if user_input:
        st.session_state["chat_history"].append(("You", user_input))
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            contract_excerpt = raw_text[:3000] if "raw_text" in locals() else ""
            prompt = f"Contract Excerpt:\n{contract_excerpt}\n\nUser: {user_input}\nAI:"
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            answer = "⚠️ Sorry, I couldn't fetch an answer right now."
        st.session_state["chat_history"].append(("AI", answer))

    st.markdown('</div>', unsafe_allow_html=True)
