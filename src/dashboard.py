# src/dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import plotly.express as px
import re
import base64
from advisor import get_advice, advisor  # Import LLM functions

# Custom CSS for modern, customer-friendly design
st.markdown(
    """
    <style>
    .logo-container {
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .header-container {
        background-color: #00695C; /* Teal background */
        padding: 10px;
        border-radius: 0 0 8px 8px;
        text-align: center; /* Center the title horizontally */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 40px;
        line-height: 40px;
    }
    .header-container h1 {
        color: white; /* White text */
        font-family: 'Roboto', sans-serif;
        margin: 0;
        font-size: 24px;
    }
    .metric-card {
        background-color: #E0E0E0; /* Light gray */
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card h3 {
        color: #424242; /* Dark gray */
        font-family: 'Roboto', sans-serif;
        margin: 0;
    }
    .metric-card p {
        color: #424242;
        font-family: 'Roboto', sans-serif;
        margin: 5px 0 0;
    }
    .section-header {
        color: #00695C;
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header with logo centered on first line and title on second line
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
logo_path = "data/finagent_logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{logo_base64}" '
        'style="display: block; margin-left: auto; margin-right: auto; max-height: 60px;" />',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<h2 style='text-align: center; color: #00695C; font-family: Roboto, sans-serif;'>📈 FinAgent</h2>",
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><h1>FinAgent Financial Dashboard</h1></div>', unsafe_allow_html=True)

# Budget Distribution and Spending Analysis in two columns
st.markdown("<h2 class='section-header'>Financial Overview</h2>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Budget Distribution (Left)
with col1:
    budget_path = "data/budget_report.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r") as f:
            budget = json.load(f)
        st.markdown("<h3 class='section-header'>Budget Distribution</h3>", unsafe_allow_html=True)
        fig = px.pie(
            values=[budget['needs']['amount'], budget['wants']['amount'], budget['savings_debt']['amount']],
            names=['Needs', 'Wants', 'Savings/Debt'],
            color_discrete_sequence=['#00695C', '#4DB6AC', '#B0BEC5'],
            title="Budget Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Budget report not found at data/budget_report.json")

# Spending Analysis (Right)
with col2:
    db_path = "data/finagent.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        report = pd.read_sql_query("SELECT * FROM monthly_reports WHERE month = '2025-06'", conn)
        conn.close()
        if not report.empty:
            st.markdown("<h3 class='section-header'>Spending Analysis</h3>", unsafe_allow_html=True)
            df = pd.read_json("data/transactions_cleaned.json")
            df['date'] = pd.to_datetime(df['date'])
            df_month = df[(df['date'].dt.year == 2025) & (df['date'].dt.month == 6) & (df['amount'] > 0)]
            spending = df_month.groupby('category')['amount'].sum().to_dict()
            st.bar_chart(spending, color="#00695C")
            st.write(f"**Risks**: {report.iloc[0]['risks']}")
            st.write(f"**Debt Strategy**: {report.iloc[0]['debt_strategy']}")
        else:
            st.error("No spending analysis found for June 2025 in data/finagent.db")
    else:
        st.error("Database not found at data/finagent.db")

# Financial Advice and Query Responses in two columns
st.markdown("<h2 class='section-header'>Guidance and Queries</h2>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

# Financial Advice (Left)
with col3:
    advice_path = "data/advice_log.json"
    if os.path.exists(advice_path):
        with open(advice_path, "r") as f:
            advice = json.load(f)
        st.markdown("<h3 class='section-header'>Financial Advice</h3>", unsafe_allow_html=True)
        llm_advice = get_advice()
        st.write(f"- {llm_advice}")
        for a in advice["advice"]:
            st.write(f"- {a}")
    else:
        st.error("Advice log not found at data/advice_log.json")

# Query Responses (Right)
with col4:
    if os.path.exists(advice_path):
        with open(advice_path, "r") as f:
            advice = json.load(f)
        st.markdown("<h3 class='section-header'>Query Responses</h3>", unsafe_allow_html=True)
        for qa in advice["qa_responses"]:
            st.write(f"**Query**: {qa['query']}")
            st.write(f"**Answer**: {qa['answer']}")
        query = st.text_input("Ask a financial question (e.g., 'What’s my best savings plan?')", key="query_input")
        if query:
            prompt = (
                f"You are a financial advisor. Answer: {query} based on spending data Needs=13.565, "
                f"Wants=97.565, Savings/Debt=25.0, and risks Low Savings/Debt spending: 0.6%."
            )
            response = advisor(prompt, max_length=150, num_return_sequences=1, temperature=0.7)[0]['generated_text']
            st.write(f"**Response**: {response.strip()}")
    else:
        st.error("Advice log not found at data/advice_log.json")