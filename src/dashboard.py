# src/dashboard.py
import streamlit as st
import base64
import os
import json
import pandas as pd
import plotly.express as px
import sqlite3

# Custom CSS for layout with green theme, 80rem max width
st.markdown(
    """
    <style>
    .main {
        max-width: 80rem; /* 1280px at 16px base font size */
        margin: 0 auto; /* Center the container */
        background-color: transparent; /* No coloring */
    }
    .dashboard-row {
        display: flex;
        align-items: center;
        max-height: 80px; /* Match logo height */
        overflow: hidden; /* Prevent overflow beyond 80px */
    }
    .logo-area {
        width: 20rem; /* 320px at 16px base font size */
        padding: 10px;
        text-align: center;
    }
    .header-area {
        flex-grow: 1;
        padding: 10px;
        background-color: #00695C; /* Green main color */
        border-radius: 8px; /* Rounded corners on all sides */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Subtle shadow for depth */
        max-height: 80px; /* Match row and logo height */
        line-height: 60px; /* Center text vertically within 80px */
        text-align: center;
        color: white; /* White text for contrast */
        font-family: 'Roboto', sans-serif; /* Professional font */
    }
    .savings-plan {
        padding: 10px;
        background-color: #E0F2F1; /* Light green background */
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# First Row: Logo and Header
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
col1, col2 = st.columns([20, 60])  # 20rem logo, remaining space for header (proportional to 80rem)
with col1:
    st.markdown('<div class="logo-area">', unsafe_allow_html=True)
    logo_path = "data/finagent_logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{logo_base64}" '
            'style="display: block; max-height: 80px; margin: auto;" />',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='font-size: 40px; color: #4CAF50;'>📈</span>",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown('<h1 class="header-area">FinAgent Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Second Row: Budget Distribution and Spending Analysis
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)  # New row for columns
col1, col2 = st.columns(2)  # Two equal-width columns
with col1:
    # Budget Distribution (Pie Chart with Dropdown)
    budget_path = "data/budget_report.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r") as f:
            budget_data = json.load(f)
        months = list(budget_data.keys())
        selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="budget_month_select")
        budget = budget_data[selected_month]
        fig = px.pie(
            values=[budget["needs"]["amount"], budget["wants"]["amount"], budget["savings_debt"]["amount"]],
            names=["Needs", "Wants", "Savings/Debt"],
            color_discrete_sequence=["#00695C", "#4CAF50", "#A5D6A7"],  # Green shades
            title=f"Budget Distribution for {selected_month}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Budget report not found at data/budget_report.json")
with col2:
    # Spending Analysis (Bar Chart with Dropdown, Risks, and Debt Strategy)
    budget_path = "data/budget_report.json"
    transactions_path = "data/transactions_cleaned.json"
    if os.path.exists(budget_path) and os.path.exists(transactions_path):
        with open(budget_path, "r") as f:
            budget_data = json.load(f)
        months = list(budget_data.keys())
        selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="spending_month_select")
        budget = budget_data[selected_month]
        st.markdown("### Spending Analysis")
        df = pd.read_json(transactions_path)
        df["date"] = pd.to_datetime(df["date"])
        df_month = df[(df["date"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M")) & (df["amount"] > 0)]
        spending = df_month.groupby("category")["amount"].sum().to_dict()
        st.bar_chart(spending, color="#00695C")
        total_spending = sum(spending.values())
        income = budget.get("income", 4000.0)
        wants_spending = spending.get("Shopping", 0) + spending.get("Entertainment", 0) + spending.get("Travel", 0)
        savings_debt_spending = spending.get("Other", 0)
        risks = "High" if wants_spending > income * 0.30 or savings_debt_spending < income * 0.20 else "Low"
        debt_strategy = f"Pay off €5000.0 in {5000.0 / max(income * 0.20 - savings_debt_spending, 1):.1f} months with €{max(income * 0.20 - savings_debt_spending, 0):.2f}/month" if income * 0.20 - savings_debt_spending > 0 else "No payoff plan; increase savings or reduce debt spending"
        st.write(f"**Risks**: {risks}")
        st.write(f"**Debt Strategy**: {debt_strategy}")
    else:
        st.error("Budget report or transactions data not found.")
st.markdown('</div>', unsafe_allow_html=True)

# Third Row: Savings Plan and LLM Query
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)  # New row for columns
col1, col2 = st.columns(2)  # Two equal-width columns
with col1:
    # Savings Plan Section
    st.markdown("### Savings Plan")
    if 'savings_plans' not in st.session_state:
        st.session_state.savings_plans = [{'goal': 0.0, 'saved': 0.0} for _ in range(4)]
    for i, plan in enumerate(st.session_state.savings_plans):
        with st.expander(f"Plan {i+1}"):
            st.markdown(f'<div class="savings-plan">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Create Plan", key=f"create_plan_{i}"):
                    goal = st.number_input("Set Goal (€)", key=f"goal_input_{i}", value=0.0)
                    plan['goal'] = goal
                if st.button("Add Saving", key=f"add_plan_{i}"):
                    amount = st.number_input("Add Amount (€)", key=f"add_input_{i}", value=0.0)
                    plan['saved'] += amount
            with col2:
                progress = plan['saved'] / max(plan['goal'], 1) if plan['goal'] > 0 else 0
                st.progress(progress)
                st.write(f"Goal: €{plan['goal']:.2f}, Saved: €{plan['saved']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
    # Save to database (placeholder for now, to be implemented)
    # conn = sqlite3.connect("data/finagent.db")
    # cursor = conn.cursor()
    # cursor.execute("CREATE TABLE IF NOT EXISTS savings_plans (plan_id INTEGER, goal REAL, saved REAL)")
    # for i, plan in enumerate(st.session_state.savings_plans):
    #     cursor.execute("INSERT OR REPLACE INTO savings_plans (plan_id, goal, saved) VALUES (?, ?, ?)", (i, plan['goal'], plan['saved']))
    # conn.commit()
    # conn.close()
# Placeholder for second column
with col2:
    st.write("LLM Query section will be implemented in the next subtask.")
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for future rows
st.write("Additional rows will be implemented as needed.")