# src/dashboard.py
import streamlit as st
import base64
import os
import json
import pandas as pd
import plotly.express as px

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

# Initialize or load balance (simulated bank balance)
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0  # Initial balance

# Load or initialize saving plans from JSON
saving_path = "data/saving.json"
if os.path.exists(saving_path):
    with open(saving_path, "r") as f:
        st.session_state.savings_plans = json.load(f)
else:
    st.session_state.savings_plans = [{'name': '', 'goal': 0.0, 'saved': 0.0} for _ in range(3)]  # Max 3 plans

# State to track creation mode and selected plan index
if 'creating_plan' not in st.session_state:
    st.session_state.creating_plan = False
if 'selected_plan_index' not in st.session_state:
    st.session_state.selected_plan_index = None

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
    budget_path = "data/budget_report.json"
    if os.path.exists(budget_path):
        with open(budget_path, "r") as f:
            budget_data = json.load(f)
        months = list(budget_data.keys())
        selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="budget_month_select")
        budget = budget_data[selected_month]
        st.markdown('<h3 class="section-header">Budget Distribution</h3>', unsafe_allow_html=True)
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
        st.markdown('<h3 class="section-header">Spending Analysis</h3>', unsafe_allow_html=True)
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
    st.markdown('<h3 class="section-header">Savings Plan</h3>', unsafe_allow_html=True)
    saving_path = "data/saving.json"
    if not os.path.exists(saving_path) or not any(plan['name'] for plan in st.session_state.savings_plans):
        col1, col2 = st.columns([3, 1])  # Adjust column ratio for layout
        with col1:
            plan_name = st.text_input("Plan Name", key="new_plan_name", value="")
        with col2:
            button_html = f'<button class="green-button" onclick="window.Streamlit.setComponentValue({{action: \'save_plan\'}})">Save Plan</button>'
            st.markdown(button_html, unsafe_allow_html=True)
            if 'save_plan_trigger' in st.session_state and st.session_state.save_plan_trigger:
                for i in range(3):
                    if st.session_state.savings_plans[i]['name'] == '':
                        st.session_state.savings_plans[i]['name'] = plan_name
                        st.session_state.savings_plans[i]['goal'] = st.number_input("Goal Amount (€)", key=f"plan_goal_{i}", value=0.0)
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plans, f)
                        st.session_state.save_plan_trigger = False
                        break
    else:
        for i, plan in enumerate(st.session_state.savings_plans):
            if plan['name']:
                st.markdown(f'<div class="savings-plan">', unsafe_allow_html=True)
                st.write(f"**{plan['name']}**")
                col1, col2 = st.columns([4, 1])  # 80% width for progress, 20% for button
                with col1:
                    progress = plan['saved'] / max(plan['goal'], 1) if plan['goal'] > 0 else 0
                    st.progress(progress, text=f"{int(progress * 100)}%")
                    st.write(f"Goal: €{plan['goal']:.2f}, Saved: €{plan['saved']:.2f}")
                with col2:
                    button_html = f'<button class="green-button" onclick="window.Streamlit.setComponentValue({{action: \'add_to_plan_{i}\'}})">Add to Plan</button>'
                    st.markdown(button_html, unsafe_allow_html=True)
                    if f'add_to_plan_{i}_trigger' in st.session_state and st.session_state[f'add_to_plan_{i}_trigger']:
                        amount = st.number_input("Add Amount (€)", key=f"add_amount_{i}", value=0.0)
                        if amount <= st.session_state.balance and amount > 0:
                            plan['saved'] += amount
                            st.session_state.balance -= amount
                            with open(saving_path, "w") as f:
                                json.dump(st.session_state.savings_plans, f)
                            st.success(f"Added €{amount:.2f} to {plan['name']}. New balance: €{st.session_state.balance:.2f}")
                        else:
                            st.error("Insufficient balance or invalid amount.")
                        st.session_state[f'add_to_plan_{i}_trigger'] = False
                st.markdown('</div>', unsafe_allow_html=True)
# Placeholder for second column
with col2:
    st.write("LLM Query section will be implemented in the next subtask.")
st.markdown('</div>', unsafe_allow_html=True)

# Handle button events
if 'save_plan_trigger' not in st.session_state:
    st.session_state.save_plan_trigger = False
for i in range(3):
    if f'add_to_plan_{i}_trigger' not in st.session_state:
        st.session_state[f'add_to_plan_{i}_trigger'] = False
if st.session_state.get('component_value'):
    action = st.session_state.component_value.get('action')
    if action == 'save_plan':
        st.session_state.save_plan_trigger = True
    elif action and action.startswith('add_to_plan_'):
        i = int(action.split('_')[-1])
        st.session_state[f'add_to_plan_{i}_trigger'] = True
    st.session_state.component_value = None

# Wrap entire dashboard content in <div class="dashboard-container">
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for future rows
st.write("Additional rows will be implemented as needed.")