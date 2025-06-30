# src/dashboard.py
import streamlit as st
import base64
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import datetime

# Custom CSS for layout with green theme, 80rem max width, and 2rem top margin
st.markdown(
    """
    <style>
    /* Target Streamlit's main content container */
    .block-container {
        max-width: 80rem !important;
        margin: 2rem auto !important; /* 2rem top margin, auto left/right for centering */
        background-color: transparent !important;
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
        font-size: 24px; /* Base size for header */
    }
    .section-header {
        font-size: 28px; /* One size bigger than header (24px + 4px) */
        color: #00695C; /* Green for section headers */
        font-family: 'Roboto', sans-serif; /* Consistent font */
        margin-bottom: 10px; /* Space below heading */
    }
    .savings-plan {
        padding: 10px;
        background-color: #E0F2F1; /* Light green background */
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .green-button {
        background-color: #00695C; /* Green/teal accent color matching header */
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-family: 'Roboto', sans-serif;
    }
    .green-button:hover {
        background-color: #004D40; /* Darker green/teal on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# File paths
saving_path = "data/saving.json"
budget_path = "data/budget_report.json"
transactions_path = "data/transactions_cleaned.json"

# Initialize or load balance and single savings plan
# File paths
saving_path = "data/saving.json"
budget_path = "data/budget_report.json"
transactions_path = "data/transactions_cleaned.json"

# Initialize or load balance and single savings plan
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0  # Initial balance
if 'savings_plan' not in st.session_state:
    st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}
if 'savings_plan' not in st.session_state:
    st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}

# Load or initialize savings plan from JSON
if os.path.exists(saving_path):
    try:
        with open(saving_path, "r") as f:
            saved_data = json.load(f)
            if isinstance(saved_data, dict) and all(key in saved_data for key in ['name', 'goal', 'saved']):
                st.session_state.savings_plan = saved_data
            else:
                st.error("Invalid savings plan format in saving.json. Resetting to default.")
                st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}
            saved_data = json.load(f)
            if isinstance(saved_data, dict) and all(key in saved_data for key in ['name', 'goal', 'saved']):
                st.session_state.savings_plan = saved_data
            else:
                st.error("Invalid savings plan format in saving.json. Resetting to default.")
                st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in saving.json. Resetting to default.")
        st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}
else:
    st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}

# Load or initialize budget and transactions data
if os.path.exists(budget_path):
    with open(budget_path, "r") as f:
        st.session_state.budget_data = json.load(f)
else:
    st.session_state.budget_data = {"2025-06": {"needs": {"amount": 1600.0}, "wants": {"amount": 1200.0}, "savings_debt": {"amount": 1200.0}, "income": 4000.0}}
if os.path.exists(transactions_path):
    with open(transactions_path, "r") as f:
        st.session_state.transactions = pd.read_json(f)
else:
    st.session_state.transactions = pd.DataFrame(columns=["date", "amount", "category"])
    st.session_state.savings_plan = {'name': '', 'goal': 0.0, 'saved': 0.0}

# Load or initialize budget and transactions data
if os.path.exists(budget_path):
    with open(budget_path, "r") as f:
        st.session_state.budget_data = json.load(f)
else:
    st.session_state.budget_data = {"2025-06": {"needs": {"amount": 1600.0}, "wants": {"amount": 1200.0}, "savings_debt": {"amount": 1200.0}, "income": 4000.0}}
if os.path.exists(transactions_path):
    with open(transactions_path, "r") as f:
        st.session_state.transactions = pd.read_json(f)
else:
    st.session_state.transactions = pd.DataFrame(columns=["date", "amount", "category"])

# Wrap entire dashboard content in <div class="dashboard-container">
# Note: Using .block-container in CSS, no explicit <div> needed

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
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="budget_month_select")
    budget = st.session_state.budget_data[selected_month]
    st.markdown('<h3 class="section-header">Budget Distribution</h3>', unsafe_allow_html=True)
    fig = px.pie(
        values=[budget["needs"]["amount"], budget["wants"]["amount"], budget["savings_debt"]["amount"]],
        names=["Needs", "Wants", "Savings/Debt"],
        color_discrete_sequence=["#00695C", "#4CAF50", "#A5D6A7"],
        title=f"Budget Distribution for {selected_month}"
    )
    st.plotly_chart(fig, use_container_width=True)
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="budget_month_select")
    budget = st.session_state.budget_data[selected_month]
    st.markdown('<h3 class="section-header">Budget Distribution</h3>', unsafe_allow_html=True)
    fig = px.pie(
        values=[budget["needs"]["amount"], budget["wants"]["amount"], budget["savings_debt"]["amount"]],
        names=["Needs", "Wants", "Savings/Debt"],
        color_discrete_sequence=["#00695C", "#4CAF50", "#A5D6A7"],
        title=f"Budget Distribution for {selected_month}"
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    # Spending Analysis (Bar Chart with Dropdown, Risks, and Debt Strategy)
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="spending_month_select")
    budget = st.session_state.budget_data[selected_month]
    st.markdown('<h3 class="section-header">Spending Analysis</h3>', unsafe_allow_html=True)
    df = st.session_state.transactions
    df["date"] = pd.to_datetime(df["date"])
    df_month = df[(df["date"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M")) & (df["amount"] > 0)]
    spending = df_month.groupby("category")["amount"].sum().to_dict()
    st.bar_chart(spending, color="#00695C")
    total_spending = sum(spending.values())
    income = budget.get("income", 4000.0)
    wants_spending = spending.get("Shopping", 0) + spending.get("Entertainment", 0) + spending.get("Travel", 0)
    savings_debt_spending = spending.get("Other", 0) + st.session_state.savings_plan.get("saved", 0)
    risks = "High" if wants_spending > income * 0.30 or savings_debt_spending < income * 0.20 else "Low"
    debt_strategy = f"Pay off €5000.0 in {5000.0 / max(income * 0.20 - savings_debt_spending, 1):.1f} months with €{max(income * 0.20 - savings_debt_spending, 0):.2f}/month" if income * 0.20 - savings_debt_spending > 0 else "No payoff plan; increase savings or reduce debt spending"
    st.write(f"**Risks**: {risks}")
    st.write(f"**Debt Strategy**: {debt_strategy}")
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="spending_month_select")
    budget = st.session_state.budget_data[selected_month]
    st.markdown('<h3 class="section-header">Spending Analysis</h3>', unsafe_allow_html=True)
    df = st.session_state.transactions
    df["date"] = pd.to_datetime(df["date"])
    df_month = df[(df["date"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M")) & (df["amount"] > 0)]
    spending = df_month.groupby("category")["amount"].sum().to_dict()
    st.bar_chart(spending, color="#00695C")
    total_spending = sum(spending.values())
    income = budget.get("income", 4000.0)
    wants_spending = spending.get("Shopping", 0) + spending.get("Entertainment", 0) + spending.get("Travel", 0)
    savings_debt_spending = spending.get("Other", 0) + st.session_state.savings_plan.get("saved", 0)
    risks = "High" if wants_spending > income * 0.30 or savings_debt_spending < income * 0.20 else "Low"
    debt_strategy = f"Pay off €5000.0 in {5000.0 / max(income * 0.20 - savings_debt_spending, 1):.1f} months with €{max(income * 0.20 - savings_debt_spending, 0):.2f}/month" if income * 0.20 - savings_debt_spending > 0 else "No payoff plan; increase savings or reduce debt spending"
    st.write(f"**Risks**: {risks}")
    st.write(f"**Debt Strategy**: {debt_strategy}")
st.markdown('</div>', unsafe_allow_html=True)

# Third Row: Savings Plan and LLM Query
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)  # New row for columns
col1, col2 = st.columns(2)  # Two equal-width columns
with col1:
    # Savings Plan Section
    st.markdown('<h3 class="section-header">Savings Plan</h3>', unsafe_allow_html=True)
    if not st.session_state.savings_plan['name']:
        with st.form(key="create_savings_plan_form"):
            st.write("Create a Savings Plan")
            plan_name = st.text_input("Plan Name", key="plan_name_input")
            plan_goal = st.number_input("Goal Amount (€)", key="plan_goal_input", value=0.0, step=1.0, format="%.0f")
            if st.form_submit_button("Save Plan"):
                if not plan_name.strip() or plan_goal < 0:
                    st.error("Plan name cannot be empty, and amount must be non-negative.")
                else:
                    st.session_state.savings_plan['name'] = plan_name.strip()
                    st.session_state.savings_plan['goal'] = plan_goal
                    # Update budget and transactions
                    current_month = "2025-06"
                    if current_month in st.session_state.budget_data:
                        st.session_state.budget_data[current_month]["savings_debt"]["amount"] += plan_goal
                        with open(budget_path, "w") as f:
                            json.dump(st.session_state.budget_data, f)
                    st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame({"date": datetime.now(), "amount": plan_goal, "category": "Savings"}, index=[0])], ignore_index=True)
                    with open(transactions_path, "w") as f:
                        st.session_state.transactions.to_json(f)
                    # Save the plan
                    try:
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plan, f)
                    except PermissionError:
                        st.error("Permission denied to write to saving.json. Please check file permissions.")
                    except Exception as e:
                        st.error(f"Failed to save plan: {e}")
                    else:
                        st.success("Plan saved successfully!")
                        st.rerun()  # Refresh the page
    if not st.session_state.savings_plan['name']:
        with st.form(key="create_savings_plan_form"):
            st.write("Create a Savings Plan")
            plan_name = st.text_input("Plan Name", key="plan_name_input")
            plan_goal = st.number_input("Goal Amount (€)", key="plan_goal_input", value=0.0, step=1.0, format="%.0f")
            if st.form_submit_button("Save Plan"):
                if not plan_name.strip() or plan_goal < 0:
                    st.error("Plan name cannot be empty, and amount must be non-negative.")
                else:
                    st.session_state.savings_plan['name'] = plan_name.strip()
                    st.session_state.savings_plan['goal'] = plan_goal
                    # Update budget and transactions
                    current_month = "2025-06"
                    if current_month in st.session_state.budget_data:
                        st.session_state.budget_data[current_month]["savings_debt"]["amount"] += plan_goal
                        with open(budget_path, "w") as f:
                            json.dump(st.session_state.budget_data, f)
                    st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame({"date": datetime.now(), "amount": plan_goal, "category": "Savings"}, index=[0])], ignore_index=True)
                    with open(transactions_path, "w") as f:
                        st.session_state.transactions.to_json(f)
                    # Save the plan
                    try:
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plan, f)
                    except PermissionError:
                        st.error("Permission denied to write to saving.json. Please check file permissions.")
                    except Exception as e:
                        st.error(f"Failed to save plan: {e}")
                    else:
                        st.success("Plan saved successfully!")
                        st.rerun()  # Refresh the page
    else:
        st.markdown(f'<div class="savings-plan">', unsafe_allow_html=True)
        st.write(f"**{st.session_state.savings_plan['name']}**")
        col1, col2 = st.columns([4, 1])
        with col1:
            progress = st.session_state.savings_plan['saved'] / max(st.session_state.savings_plan['goal'], 1) if st.session_state.savings_plan['goal'] > 0 else 0
            st.progress(progress, text=f"{int(progress * 100)}%")
            st.write(f"Goal: €{st.session_state.savings_plan['goal']:.2f}, Saved: €{st.session_state.savings_plan['saved']:.2f}")
            st.write(f"Remaining Balance: €{st.session_state.balance:.2f}")
        with col2:
            amount = st.number_input("Add Amount (€)", key="add_amount_input", value=0.0, step=1.0, format="%.0f")  # Pre-filled input
            if st.button("Add to Plan", key="add_to_plan_button"):
                if amount <= st.session_state.balance and amount > 0:
                    st.session_state.savings_plan['saved'] += amount
                    st.session_state.balance -= amount
                    # Update budget and transactions
                    current_month = "2025-06"
                    if current_month in st.session_state.budget_data:
                        st.session_state.budget_data[current_month]["savings_debt"]["amount"] += amount
                        with open(budget_path, "w") as f:
                            json.dump(st.session_state.budget_data, f)
                    st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame({"date": datetime.now(), "amount": amount, "category": "Savings"}, index=[0])], ignore_index=True)
                    with open(transactions_path, "w") as f:
                        st.session_state.transactions.to_json(f)
                    # Save the updated plan
                    try:
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plan, f)
                    except PermissionError:
                        st.error("Permission denied to write to saving.json. Please check file permissions.")
                    except Exception as e:
                        st.error(f"Failed to update savings plan: {e}")
                    else:
                        st.success(f"Added €{amount:.2f} to {st.session_state.savings_plan['name']}. New balance: €{st.session_state.balance:.2f}")
                        st.rerun()  # Refresh the page
                else:
                    st.error("Insufficient balance or invalid amount.")
        st.markdown('</div>', unsafe_allow_html=True)
# Placeholder for second column
with col2:
    st.write("LLM Query section will be implemented in the next subtask.")
st.markdown('</div>', unsafe_allow_html=True)

# Wrap entire dashboard content in <div class="dashboard-container">
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for future rows
st.write("Additional rows will be implemented as needed.")