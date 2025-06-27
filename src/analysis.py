# src/analysis.py
import pandas as pd
import sqlite3
from datetime import datetime

def analyze_spending(income, clean_input_path="data/transactions_cleaned.json"):
    """Analyze spending habits, flag risks, and calculate debt payoff plan."""
    try:
        # Load cleaned transactions
        df = pd.read_json(clean_input_path)
        print("Analyzing spending for all months...")

        # Convert date to datetime and extract unique months
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        unique_months = df['date'].dt.to_period('M').unique()

        analysis_reports = {}

        for month in unique_months:
            month_str = month.strftime("%Y-%m")
            df_month = df[df['date'].dt.to_period('M') == month]

            # Spending analysis
            total_spending = df_month[df_month['amount'] > 0]['amount'].sum()
            avg_spending = total_spending / len(df_month) if len(df_month) > 0 else 0

            # Risk flagging (e.g., high spending in wants or low savings)
            wants_spending = df_month[df_month['category'].isin(['Shopping', 'Entertainment', 'Travel']) & (df_month['amount'] > 0)]['amount'].sum()
            savings_debt_spending = df_month[df_month['category'] == 'Other']['amount'].sum()
            risk = "High" if wants_spending > income * 0.30 or savings_debt_spending < income * 0.20 else "Low"

            # Simple debt payoff plan (assuming initial debt of €5000, paid from savings)
            initial_debt = 5000.0
            monthly_saving = max(income * 0.20 - savings_debt_spending, 0)  # Savings after debt spending
            months_to_payoff = initial_debt / monthly_saving if monthly_saving > 0 else float('inf')
            debt_strategy = (
                f"Pay off €{initial_debt:.2f} in {months_to_payoff:.1f} months with €{monthly_saving:.2f}/month"
                if monthly_saving > 0 else "No payoff plan; increase savings or reduce debt spending"
            )

            # Save to SQLite
            conn = sqlite3.connect("data/finagent.db")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS monthly_reports
                            (month TEXT PRIMARY KEY, income REAL, needs_amount REAL, wants_amount REAL, 
                            savings_debt_amount REAL, total_spending REAL, avg_spending REAL, risks TEXT, debt_strategy TEXT)''')
            cursor.execute('''INSERT OR REPLACE INTO monthly_reports 
                            (month, income, needs_amount, wants_amount, savings_debt_amount, total_spending, 
                            avg_spending, risks, debt_strategy)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (month_str, income, df_month[df_month['category'].isin(['Bills', 'Transportation', 'Food']) & (df_month['amount'] > 0)]['amount'].sum(),
                            wants_spending, savings_debt_spending, total_spending, avg_spending, risk, debt_strategy))
            conn.commit()
            conn.close()

            # Create analysis report
            analysis_reports[month_str] = {
                "income": income,
                "total_spending": total_spending,
                "avg_spending": avg_spending,
                "risks": risk,
                "debt_strategy": debt_strategy
            }
            print(f"Spending Analysis Report for {month_str}: {analysis_reports[month_str]}")

        return analysis_reports

    except Exception as e:
        print(f"Error analyzing spending: {e}")
        return {}