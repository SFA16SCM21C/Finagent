import streamlit as st
import pandas as pd
import sqlite3
import json
import os

# Custom CSS for title styling
st.markdown(
    """
    <style>
    .title-container {
        background-color: #2E7D32; /* Green background */
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .title-container h1 {
        color: white; /* White text */
        margin: 0;
    }
    .metric-box {
        background-color: #F5F5F5;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title with green background and white text
st.markdown(
    '<div class="title-container"><h1>FinAgent Financial Dashboard</h1></div>',
    unsafe_allow_html=True
)

# Logo (placeholder, replace with actual logo path)
logo_path = "data/finagent_logo.png"  # Replace with your logo file
if os.path.exists(logo_path):
    st.image(logo_path, width=150)
else:
    st.warning("Logo not found at data/finagent_logo.png. Please add a logo file.")

# Budget Summary in two-column layout
budget_path = "data/budget_report.json"
if os.path.exists(budget_path):
    with open(budget_path, "r") as f:
        budget = json.load(f)

    st.header("Budget Summary (June 2025)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="metric-box"><strong>Income</strong><br>${budget["income"]:.2f}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="metric-box"><strong>Needs</strong><br>${budget["needs"]["amount"]:.2f} ({budget["needs"]["percentage"]:.1f}%, {budget["needs"]["status"]})</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="metric-box"><strong>Wants</strong><br>${budget["wants"]["amount"]:.2f} ({budget["wants"]["percentage"]:.1f}%, {budget["wants"]["status"]})</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="metric-box"><strong>Savings/Debt</strong><br>${budget["savings_debt"]["amount"]:.2f} ({budget["savings_debt"]["percentage"]:.1f}%, {budget["savings_debt"]["status"]})</div>',
            unsafe_allow_html=True
        )
else:
    st.error("Budget report not found at data/budget_report.json")

# Spending Analysis and Financial Advice in two-column layout
st.header("Analysis and Advice")
col3, col4 = st.columns(2)

# Spending Analysis (Left)
with col3:
    db_path = "data/finagent.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        report = pd.read_sql_query("SELECT * FROM monthly_reports WHERE month = '2025-06'", conn)
        conn.close()

        if not report.empty:
            st.subheader("Spending Analysis")
            # Hardcoded spending (to be replaced with dynamic data)
            spending = {
                "Food": 16.33,
                "Shopping": 89.40,
                "Transportation": 5.40,
                "Other": 25.00
            }
            st.bar_chart(spending)
            st.write(f"**Risks**: {report.iloc[0]['risks']}")
            st.write(f"**Debt Strategy**: {report.iloc[0]['debt_strategy']}")
        else:
            st.error("No spending analysis found for June 2025 in data/finagent.db")
    else:
        st.error("Database not found at data/finagent.db")

# Financial Advice (Right)
with col4:
    advice_path = "data/advice_log.json"
    if os.path.exists(advice_path):
        with open(advice_path, "r") as f:
            advice = json.load(f)

        st.subheader("Financial Advice")
        for a in advice["advice"]:
            st.write(f"- {a}")
    else:
        st.error("Advice log not found at data/advice_log.json")

# Query Responses (Bottom)
st.header("Query Responses")
if os.path.exists(advice_path):
    with open(advice_path, "r") as f:
        advice = json.load(f)

    for qa in advice["qa_responses"]:
        st.write(f"**Query**: {qa['query']}")
        st.write(f"**Answer**: {qa['answer']}")
else:
    st.error("Advice log not found at data/advice_log.json")