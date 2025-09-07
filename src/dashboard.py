import streamlit as st
import base64
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# Custom CSS for layout with green theme, 98rem max width, and 2rem top margin
st.markdown(
    """
    <style>
    /* Target Streamlit's main content container */
    .block-container {
        max-width: 98rem !important;
        margin: -5rem auto !important;
        background-color: transparent !important;
    }
    .dashboard-row {
        display: flex;
        align-items: center;
        max-height: 80px;
        overflow: hidden;
    }
    .logo-area {
        width: 5rem;
        padding: 10px;
        text-align: center;
    }
    .header-area {
        flex-grow: 1;
        padding: 10px;
        background-color: #0c49a6;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        max-height: 80px;
        line-height: 60px;
        text-align: center;
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: 24px;
    }
    .section-header {
        font-size: 28px;
        color: #0c49a6;
        font-family: 'Roboto', sans-serif;
        margin-bottom: 10px;
    }
    button[data-testid="stFormSubmitButton"]#save_plan_button {
        background-color: #0c49a6 !important;
        color: white !important;
        padding: 5px 15px !important;
        border-radius: 5px !important;
        border: none !important;
        cursor: pointer !important;
        font-family: 'Roboto', sans-serif !important;
    }
    button[data-testid="stFormSubmitButton"]#save_plan_button:hover {
        background-color: #2c75d4 !important;
    }
    button[data-testid="stButton"]#add_to_plan_button {
        background-color: #002769 !important;
        color: white !important;
        padding: 5px 15px !important;
        border-radius: 5px !important;
        border: none !important;
        cursor: pointer !important;
        font-family: 'Roboto', sans-serif !important;
    }
    button[data-testid="stButton"]#add_to_plan_button:hover {
        background-color: #2c75d4 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# File paths
saving_path = "data/saving.json"
budget_path = "data/budget_report.json"
transactions_path = "data/transactions_cleaned.json"

# Initialize or load balance and single savings plan
if "balance" not in st.session_state:
    st.session_state.balance = 10000.0
if "savings_plan" not in st.session_state:
    st.session_state.savings_plan = {"name": "", "goal": 0.0, "saved": 0.0}

# Load or initialize savings plan from JSON
if os.path.exists(saving_path):
    try:
        with open(saving_path, "r") as f:
            saved_data = json.load(f)
            if isinstance(saved_data, dict) and all(
                key in saved_data for key in ["name", "goal", "saved"]
            ):
                st.session_state.savings_plan = saved_data
            else:
                st.error(
                    "Invalid savings plan format in saving.json. Resetting to default."
                )
                st.session_state.savings_plan = {"name": "", "goal": 0.0, "saved": 0.0}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in saving.json. Resetting to default.")
        st.session_state.savings_plan = {"name": "", "goal": 0.0, "saved": 0.0}
else:
    st.session_state.savings_plan = {"name": "", "goal": 0.0, "saved": 0.0}

# Load or initialize budget and transactions data
if os.path.exists(budget_path):
    with open(budget_path, "r") as f:
        st.session_state.budget_data = json.load(f)
else:
    st.session_state.budget_data = {
        "2025-06": {
            "needs": {"amount": 1600.0},
            "wants": {"amount": 1200.0},
            "savings_debt": {"amount": 1200.0},
            "income": 4000.0,
        }
    }
if os.path.exists(transactions_path):
    with open(transactions_path, "r") as f:
        st.session_state.transactions_data = (
            json.load(f) if os.path.getsize(transactions_path) > 0 else []
        )
else:
    st.session_state.transactions_data = []

# First Row: Logo and Header
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
col1, col2 = st.columns([10, 70])
with col1:
    st.markdown('<div class="logo-area">', unsafe_allow_html=True)
    logo_path = "data/finagent_logo.jpg"
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
            "<span style='font-size: 40px; color: #4c6daf;'>📈</span>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div>", unsafe_allow_html=True)
    st.markdown(
        '<h1 class="header-area">FinAgent Dashboard</h1>', unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Second Row: Budget Distribution and Spending Analysis
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    # Budget Distribution (Pie Chart with Dropdown)
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox(
        "Select Month",
        months,
        index=months.index("2025-06") if "2025-06" in months else 0,
        key="budget_month_select",
    )
    budget = st.session_state.budget_data[selected_month]
    st.markdown(
        '<h3 class="section-header">Budget Distribution</h3>', unsafe_allow_html=True
    )
    fig = px.pie(
        values=[
            budget["needs"]["amount"],
            budget["wants"]["amount"],
            budget["savings_debt"]["amount"],
        ],
        names=["Needs", "Wants", "Savings/Debt"],
        color_discrete_sequence=["#002769", "#4c68af", "#a5b1d6"],
        title=f"Budget Distribution for {selected_month}",
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    # Spending Analysis (Bar Chart with Dropdown, Risks, and Debt Strategy)
    months = list(st.session_state.budget_data.keys())
    selected_month = st.selectbox(
        "Select Month",
        months,
        index=months.index("2025-06") if "2025-06" in months else 0,
        key="spending_month_select",
    )
    budget = st.session_state.budget_data[selected_month]
    st.markdown(
        '<h3 class="section-header">Spending Analysis</h3>', unsafe_allow_html=True
    )
    transactions_df = pd.DataFrame(st.session_state.transactions_data)
    transactions_df["date"] = pd.to_datetime(transactions_df["date"])
    df_month = transactions_df[
        (
            transactions_df["date"].dt.to_period("M")
            == pd.to_datetime(selected_month).to_period("M")
        )
        & (transactions_df["amount"] > 0)
    ]
    spending = df_month.groupby("category")["amount"].sum().to_dict()
    st.bar_chart(spending, color="#002a69")
    total_spending = sum(spending.values())
    income = budget.get("income", 4000.0)
    wants_spending = (
        spending.get("Shopping", 0)
        + spending.get("Entertainment", 0)
        + spending.get("Travel", 0)
    )
    savings_debt_spending = spending.get(
        "Other", 0
    ) + st.session_state.savings_plan.get("saved", 0)
    risks = (
        "High"
        if wants_spending > income * 0.30 or savings_debt_spending < income * 0.20
        else "Low"
    )
    debt_strategy = (
        f"Pay off €5000.0 in {5000.0 / max(income * 0.20 - savings_debt_spending, 1):.1f} months with €{max(income * 0.20 - savings_debt_spending, 0):.2f}/month"
        if income * 0.20 - savings_debt_spending > 0
        else "No payoff plan; increase savings or reduce debt spending"
    )
    st.write(f"**Risks**: {risks}")
    st.write(f"**Debt Strategy**: {debt_strategy}")
st.markdown("</div>", unsafe_allow_html=True)

# Third Row: Savings Plan and Dynamic Spending Insights
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    # Savings Plan Section
    st.markdown('<h3 class="section-header">Savings Plan</h3>', unsafe_allow_html=True)
    if not st.session_state.savings_plan["name"]:
        with st.form(key="create_savings_plan_form"):
            st.write("Create a Savings Plan")
            plan_name = st.text_input("Plan Name", key="plan_name_input")
            plan_goal = st.number_input(
                "Goal Amount (€)",
                key="plan_goal_input",
                value=0.0,
                step=1.0,
                format="%.0f",
            )
            if st.form_submit_button(
                "Save Plan", key="save_plan_button", help="Save the new savings plan"
            ):
                if not plan_name.strip() or plan_goal < 0:
                    st.error(
                        "Plan name cannot be empty, and amount must be non-negative."
                    )
                else:
                    st.session_state.savings_plan["name"] = plan_name.strip()
                    st.session_state.savings_plan["goal"] = plan_goal
                    current_month = "2025-06"
                    if current_month in st.session_state.budget_data:
                        st.session_state.budget_data[current_month]["savings_debt"][
                            "amount"
                        ] += plan_goal
                        with open(budget_path, "w") as f:
                            json.dump(st.session_state.budget_data, f, indent=4)
                    txn_id = f"txn_{int(datetime.now().timestamp())}"
                    new_transaction = {
                        "txnId": txn_id,
                        "date": datetime.now().isoformat(),
                        "amount": plan_goal,
                        "category": "Savings",
                    }
                    st.session_state.transactions_data.append(new_transaction)
                    with open(transactions_path, "w") as f:
                        json.dump(st.session_state.transactions_data, f, indent=4)
                    try:
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plan, f, indent=4)
                        st.success("Plan saved successfully!")
                    except PermissionError:
                        st.error(
                            "Permission denied to write to saving.json. Check file permissions."
                        )
                    except Exception as e:
                        st.error(f"Failed to save plan: {e}")
                    else:
                        st.rerun()
    else:
        st.markdown(f'<div class="savings-plan">', unsafe_allow_html=True)
        st.write(f"**{st.session_state.savings_plan['name']}**")
        col_1, col_2 = st.columns([3, 1])
        with col_1:
            progress = (
                st.session_state.savings_plan["saved"]
                / max(st.session_state.savings_plan["goal"], 1)
                if st.session_state.savings_plan["goal"] > 0
                else 0
            )
            st.progress(progress, text=f"{int(progress * 100)}%")
            st.write(
                f"Goal: €{st.session_state.savings_plan['goal']:.2f}, Saved: €{st.session_state.savings_plan['saved']:.2f}"
            )
            st.write(f"Remaining Balance: €{st.session_state.balance:.2f}")
        with col_2:
            amount = st.number_input(
                "Add Amount (€)",
                key="add_amount_input",
                value=0.0,
                step=1.0,
                format="%.0f",
            )
            if st.button("Add to Plan", key="add_to_plan_button"):
                if amount <= st.session_state.balance and amount > 0:
                    st.session_state.savings_plan["saved"] += amount
                    st.session_state.balance -= amount
                    current_month = "2025-06"
                    if current_month in st.session_state.budget_data:
                        st.session_state.budget_data[current_month]["savings_debt"][
                            "amount"
                        ] += amount
                        with open(budget_path, "w") as f:
                            json.dump(st.session_state.budget_data, f, indent=4)
                    txn_id = f"txn_{int(datetime.now().timestamp())}"
                    new_transaction = {
                        "txnId": txn_id,
                        "date": datetime.now().isoformat(),
                        "amount": amount,
                        "category": "Savings",
                    }
                    st.session_state.transactions_data.append(new_transaction)
                    with open(transactions_path, "w") as f:
                        json.dump(st.session_state.transactions_data, f, indent=4)
                    try:
                        with open(saving_path, "w") as f:
                            json.dump(st.session_state.savings_plan, f, indent=4)
                        st.success(
                            f"Added €{amount:.2f} to {st.session_state.savings_plan['name']}. New balance: €{st.session_state.balance:.2f}"
                        )
                    except PermissionError:
                        st.error(
                            "Permission denied to write to saving.json. Check file permissions."
                        )
                    except Exception as e:
                        st.error(f"Failed to update savings plan: {e}")
                    else:
                        st.rerun()
                else:
                    st.error("Insufficient balance or invalid amount.")
        st.markdown("</div>", unsafe_allow_html=True)
with col2:
    # Dynamic Spending Insights with Dropdowns and Advice
    st.markdown('<h4 style="color: #0c49a6; font-family: Roboto, sans-serif;">Dynamic Spending Insights</h4>', unsafe_allow_html=True)
    st.write("Select a query type and month to view financial recommendations.")
    col1, col2 = st.columns([1, 1])
    with col1:
        query_types = [
            "Spending Analysis",
            "Savings Progress",
            "Overspending Analysis",
            "Budget Distribution",
            "Transaction Summary"
        ]
        selected_query = st.selectbox("Select Query Type", query_types, key="query_type_select")
    with col2:
        months = list(st.session_state.budget_data.keys())
        selected_month = st.selectbox("Select Month", months, index=months.index("2025-06") if "2025-06" in months else 0, key="month_select")
    
    # Generate and display advice
    transactions_df = pd.DataFrame(st.session_state.transactions_data or [])
    transactions_df["date"] = pd.to_datetime(transactions_df["date"], errors="coerce")
    budget = st.session_state.budget_data[selected_month]
    df_month = transactions_df[
        (
            transactions_df["date"].dt.to_period("M")
            == pd.to_datetime(selected_month).to_period("M")
        )
        & (transactions_df["amount"] > 0)
    ]
    spending = df_month.groupby("category")["amount"].sum().to_dict()
    total_spending = df_month["amount"].sum()
    income = budget.get("income", 4000.0)
    wants_spending = (
        spending.get("Shopping", 0)
        + spending.get("Entertainment", 0)
        + spending.get("Travel", 0)
    )
    savings_debt_spending = spending.get("Other", 0) + st.session_state.savings_plan.get("saved", 0)
    savings_progress = (
        st.session_state.savings_plan["saved"]
        / max(st.session_state.savings_plan["goal"], 1)
        * 100
        if st.session_state.savings_plan["goal"] > 0
        else 0
    )
    avg_spending = total_spending / len(df_month) if len(df_month) > 0 else 0
    top_category = max(spending.items(), key=lambda x: x[1], default=("None", 0))

    st.markdown(f"**{selected_query} Recommendation for {selected_month}:**")
    if selected_query == "Spending Analysis":
        st.write(f"Your total spending of €{total_spending:.2f} is {'' if total_spending <= income else 'above '}your income of €{income:.2f}. Consider reviewing high-spend categories like {top_category[0]} (€{top_category[1]:.2f}).")
    elif selected_query == "Savings Progress":
        st.write(f"You've saved €{st.session_state.savings_plan['saved']:.2f} toward your €{st.session_state.savings_plan['goal']:.2f} goal ({savings_progress:.1f}%). Increase contributions by €{(st.session_state.savings_plan['goal'] - st.session_state.savings_plan['saved']) / 12:.2f}/month to meet it in a year.")
    elif selected_query == "Overspending Analysis":
        if wants_spending > income * 0.30:
            st.write(f"Your wants spending (€{wants_spending:.2f}) exceeds 30% of your income (€{income * 0.30:.2f}). Reduce discretionary expenses to stay within budget.")
        else:
            st.write(f"Your wants spending (€{wants_spending:.2f}) is within 30% of your income. Maintain this to avoid overspending.")
    elif selected_query == "Budget Distribution":
        st.write(f"Your budget allocates €{budget['needs']['amount']:.2f} to needs, €{budget['wants']['amount']:.2f} to wants, and €{budget['savings_debt']['amount']:.2f} to savings/debt. Ensure savings/debt allocation remains at least 20% of income (€{income * 0.20:.2f}).")
    elif selected_query == "Transaction Summary":
        st.write(f"You spent €{total_spending:.2f} across {len(df_month)} transactions, averaging €{avg_spending:.2f} per transaction. Focus on reducing spending in {top_category[0]} (€{top_category[1]:.2f}) to optimize your budget.")
st.markdown("</div>", unsafe_allow_html=True)

# Close dashboard container
st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<h1 class="header-area"></h1>', unsafe_allow_html=True)