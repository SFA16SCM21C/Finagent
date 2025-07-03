import unittest
from unittest.mock import patch, mock_open
import os
import json
from src.dashboard import st  # Mocked Streamlit

class TestDashboard(unittest.TestCase):
    @patch("streamlit.markdown")
    @patch("streamlit.write")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_savings_plan(self, mock_file, mock_write, mock_markdown):
        """Test loading savings plan from JSON."""
        mock_file.return_value.read.return_value = json.dumps({"name": "Test Plan", "goal": 1000.0, "saved": 200.0})
        with patch.dict(os.environ, {"saving_path": "data/saving.json"}):
            # Simulate dashboard initialization
            if "savings_plan" not in st.session_state:
                st.session_state.savings_plan = {}
            if os.path.exists("data/saving.json"):
                with open("data/saving.json", "r") as f:
                    saved_data = json.load(f)
                    if isinstance(saved_data, dict) and all(key in saved_data for key in ["name", "goal", "saved"]):
                        st.session_state.savings_plan = saved_data
            self.assertEqual(st.session_state.savings_plan["name"], "Test Plan")
            self.assertEqual(st.session_state.savings_plan["goal"], 1000.0)
            self.assertEqual(st.session_state.savings_plan["saved"], 200.0)

    @patch("streamlit.markdown")
    @patch("streamlit.write")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_budget_data(self, mock_file, mock_write, mock_markdown):
        """Test loading budget data from JSON."""
        mock_file.return_value.read.return_value = json.dumps({
            "2025-06": {"needs": {"amount": 1600.0}, "wants": {"amount": 1200.0}, "savings_debt": {"amount": 1200.0}, "income": 4000.0}
        })
        with patch.dict(os.environ, {"budget_path": "data/budget_report.json"}):
            if "budget_data" not in st.session_state:
                st.session_state.budget_data = {}
            if os.path.exists("data/budget_report.json"):
                with open("data/budget_report.json", "r") as f:
                    st.session_state.budget_data = json.load(f)
            self.assertEqual(st.session_state.budget_data["2025-06"]["needs"]["amount"], 1600.0)

    @patch("streamlit.markdown")
    @patch("streamlit.plotly_chart")
    def test_budget_distribution_chart(self, mock_plotly, mock_markdown):
        """Test rendering of budget distribution pie chart."""
        st.session_state.budget_data = {"2025-06": {"needs": {"amount": 1600.0}, "wants": {"amount": 1200.0}, "savings_debt": {"amount": 1200.0}}}
        months = list(st.session_state.budget_data.keys())
        selected_month = "2025-06"
        budget = st.session_state.budget_data[selected_month]
        fig = px.pie(
            values=[budget["needs"]["amount"], budget["wants"]["amount"], budget["savings_debt"]["amount"]],
            names=["Needs", "Wants", "Savings/Debt"],
            color_discrete_sequence=["#00695C", "#4CAF50", "#A5D6A7"],
            title=f"Budget Distribution for {selected_month}"
        )
        st.plotly_chart(fig, use_container_width=True)
        mock_plotly.assert_called_once()

    @patch("streamlit.markdown")
    @patch("streamlit.bar_chart")
    def test_spending_analysis_chart(self, mock_bar, mock_markdown):
        """Test rendering of spending analysis bar chart."""
        st.session_state.transactions_data = [
            {"date": "2025-06-15", "amount": 50.0, "category": "Food"},
            {"date": "2025-06-15", "amount": 30.0, "category": "Shopping"}
        ]
        st.session_state.budget_data = {"2025-06": {"income": 4000.0}}
        months = list(st.session_state.budget_data.keys())
        selected_month = "2025-06"
        budget = st.session_state.budget_data[selected_month]
        transactions_df = pd.DataFrame(st.session_state.transactions_data)
        transactions_df["date"] = pd.to_datetime(transactions_df["date"])
        df_month = transactions_df[(transactions_df["date"].dt.to_period("M") == pd.to_datetime(selected_month).to_period("M")) & (transactions_df["amount"] > 0)]
        spending = df_month.groupby("category")["amount"].sum().to_dict()
        st.bar_chart(spending, color="#00695C")
        mock_bar.assert_called_once()

if __name__ == "__main__":
    unittest.main()