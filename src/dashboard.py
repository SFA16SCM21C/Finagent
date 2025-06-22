import streamlit as st
import pandas as pd
import sqlite3
import json
import os

# Set page title
st.title("FinAgent Financial Dashboard")

# Load budget report
budget_path = "data/budget_report.json"
if os.path.exists(budget_path):
    with open(budget_path, "r") as f:
        budget = json.load(f)

    st.header("Budget Summary (June 2025)")
    st.write(f"Income: ${budget['income']:.2f}")
    st.write(f"Needs: ${budget['needs']['amount']:.2f} ({budget['needs']['percentage']:.1f}%, {budget['needs']['status']})")
    st.write(f"Wants: ${budget['wants']['amount']:.2f} ({budget['wants']['percentage']:.1f}%, {budget['wants']['status']})")
    st.write(f"Savings/Debt: ${budget['savings_debt']['amount']:.2f} ({budget['savings_debt']['percentage']:.1f}%, {budget['savings_debt']['status']})")
else:
    st.error("Budget report not found at data/budget_report.json")

# Load spending analysis from SQLite
db_path = "data/finagent.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    report = pd.read_sql_query("SELECT * FROM monthly_reports WHERE month = '2025-06'", conn)
    conn.close()

    if not report.empty:
        st.header("Spending Analysis")
        # Hardcoded spending for now, to be replaced with dynamic data
        spending = {
            "Food": 16.33,
            "Shopping": 89.40,
            "Transportation": 5.40,
            "Other": 25.00
        }
        st.bar_chart(spending)
        st.write(f"Risks: {report.iloc[0]['risks']}")
        st.write(f"Debt Strategy: {report.iloc[0]['debt_strategy']}")
    else:
        st.error("No spending analysis found for June 2025 in data/finagent.db")
else:
    st.error("Database not found at data/finagent.db")

# Load advice
advice_path = "data/advice_log.json"
if os.path.exists(advice_path):
    with open(advice_path, "r") as f:
        advice = json.load(f)

    st.header("Financial Advice")
    for a in advice["advice"]:
        st.write(f"- {a}")
    st.header("Query Responses")
    for qa in advice["qa_responses"]:
        st.write(f"Query: {qa['query']}")
        st.write(f"Answer: {qa['answer']}")
else:
    st.error("Advice log not found at data/advice_log.json")