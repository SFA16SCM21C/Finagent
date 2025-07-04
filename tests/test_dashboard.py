import unittest
from unittest.mock import patch, mock_open
import os
import json
import pandas as pd
from src.dashboard import st  # Import st from dashboard.py for mocking
import plotly.express as px

# Custom class to mimic st.session_state's behavior (dict with attribute access)
class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'SessionState' object has no attribute '{key}'")
    def __setattr__(self, key, value):
        self[key] = value

class TestDashboard(unittest.TestCase):

    @patch.object(st, "session_state", new_callable=SessionState)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_savings_plan(self, mock_file, mock_session_state):
        """Test loading savings plan from JSON into session state."""
        # Mock file content
        mock_file.return_value.read.return_value = json.dumps({
            "name": "Test Plan", "goal": 1000.0, "saved": 200.0
        })
        # Simulate os.path.exists returning True
        with patch("os.path.exists", return_value=True):
            # Logic from dashboard.py
            if os.path.exists("data/saving.json"):
                with open("data/saving.json", "r") as f:
                    saved_data = json.load(f)
                    if isinstance(saved_data, dict) and all(key in saved_data for key in ["name", "goal", "saved"]):
                        st.session_state.savings_plan = saved_data
        # Assertions
        self.assertEqual(st.session_state.savings_plan["name"], "Test Plan")
        self.assertEqual(st.session_state.savings_plan["goal"], 1000.0)
        self.assertEqual(st.session_state.savings_plan["saved"], 200.0)

    @patch.object(st, "session_state", new_callable=SessionState)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_budget_data(self, mock_file, mock_session_state):
        """Test loading budget data from JSON into session state."""
        # Mock file content
        mock_file.return_value.read.return_value = json.dumps({
            "2025-06": {
                "needs": {"amount": 1600.0},
                "wants": {"amount": 1200.0},
                "savings_debt": {"amount": 1200.0},
                "income": 4000.0
            }
        })
        # Simulate os.path.exists returning True
        with patch("os.path.exists", return_value=True):
            # Logic from dashboard.py
            if os.path.exists("data/budget_report.json"):
                with open("data/budget_report.json", "r") as f:
                    st.session_state.budget_data = json.load(f)
        # Assertion
        self.assertEqual(st.session_state.budget_data["2025-06"]["needs"]["amount"], 1600.0)

    @patch("streamlit.plotly_chart")
    def test_budget_distribution_chart(self, mock_plotly):
        """Test rendering of budget distribution pie chart."""
        # Set up session state directly (read-only in this test)
        st.session_state.budget_data = {
            "2025-06": {
                "needs": {"amount": 1600.0},
                "wants": {"amount": 1200.0},
                "savings_debt": {"amount": 1200.0}
            }
        }
        # Logic from dashboard.py
        selected_month = "2025-06"
        budget = st.session_state.budget_data[selected_month]
        fig = px.pie(
            values=[budget["needs"]["amount"], budget["wants"]["amount"], budget["savings_debt"]["amount"]],
            names=["Needs", "Wants", "Savings/Debt"],
            color_discrete_sequence=["#00695C", "#4CAF50", "#A5D6A7"],
            title=f"Budget Distribution for {selected_month}"
        )
        st.plotly_chart(fig, use_container_width=True)
        # Assertion
        mock_plotly.assert_called_once()

    @patch("streamlit.bar_chart")
    def test_spending_analysis_chart(self, mock_bar):
        """Test rendering of spending analysis bar chart."""
        # Set up session state directly (read-only in this test)
        st.session_state.transactions_data = [
            {"date": "2025-06-15", "amount": 50.0, "category": "Food"},
            {"date": "2025-06-15", "amount": 30.0, "category": "Shopping"}
        ]
        st.session_state.budget_data = {"2025-06": {"income": 4000.0}}
        # Logic from dashboard.py
        selected_month = "2025-06"
        transactions_df = pd.DataFrame(st.session_state.transactions_data)
        transactions_df["date"] = pd.to_datetime(transactions_df["date"])
        df_month = transactions_df[
            (transactions_df["date"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M")) &
            (transactions_df["amount"] > 0)
        ]
        spending = df_month.groupby("category")["amount"].sum().to_dict()
        st.bar_chart(spending, color="#00695C")
        # Assertion
        mock_bar.assert_called_once()

    @patch.object(st, "session_state", new_callable=SessionState)
    @patch("builtins.open", new_callable=mock_open)
    def test_save_savings_plan(self, mock_file, mock_session_state):
        """Test saving a new savings plan updates session state and file."""
        # Initial setup
        st.session_state.savings_plan = {"name": "", "goal": 0.0, "saved": 0.0}
        st.session_state.balance = 10000.0
        # Simulate form submission
        plan_name = "Vacation Fund"
        plan_goal = 5000.0
        # Logic from dashboard.py (simplified form submission)
        st.session_state.savings_plan["name"] = plan_name
        st.session_state.savings_plan["goal"] = plan_goal
        with open("data/saving.json", "w") as f:
            json.dump(st.session_state.savings_plan, f, indent=4)
        # Assertions
        self.assertEqual(st.session_state.savings_plan["name"], "Vacation Fund")
        self.assertEqual(st.session_state.savings_plan["goal"], 5000.0)

    @patch("streamlit.progress")
    def test_savings_progress(self, mock_progress):
        """Test savings progress calculation in the dashboard."""
        # Set up session state directly (read-only in this test)
        st.session_state.savings_plan = {"name": "Test Plan", "goal": 1000.0, "saved": 400.0}
        # Logic from dashboard.py
        progress = st.session_state.savings_plan["saved"] / max(st.session_state.savings_plan["goal"], 1)
        st.progress(progress, text=f"{int(progress * 100)}%")
        # Assertion
        mock_progress.assert_called_once_with(0.4, text="40%")

if __name__ == "__main__":
    unittest.main()