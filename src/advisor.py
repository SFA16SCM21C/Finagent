# src/advisor.py
from transformers import pipeline
import sqlite3
import pandas as pd
import json

try:
    advisor = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")
except Exception as e:
    print(f"Failed to load gpt-neo-125M: {e}. Using gpt2 instead.")
    advisor = pipeline("text-generation", model="gpt2")

def generate_advice(spending_data, risks):
    """Generate financial advice based on spending data and risks."""
    prompt = f"Based on spending data {spending_data} and risks {risks}, suggest a financial plan. Keep it concise and actionable."
    response = advisor(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
    return response.strip()

def get_advice(month="2025-06"):
    """Fetch advice for a specific month from database."""
    conn = sqlite3.connect("data/finagent.db")
    report = pd.read_sql_query(f"SELECT * FROM monthly_reports WHERE month = '{month}'", conn)
    conn.close()
    if not report.empty:
        spending = {
            "Needs": report.iloc[0]['needs_amount'],
            "Wants": report.iloc[0]['wants_amount'],
            "Savings/Debt": report.iloc[0]['savings_debt_amount']
        }
        risks = report.iloc[0]['risks']
        return generate_advice(spending, risks)
    return "No data available for advice."

def get_rule_based_advice():
    with open("data/advice_log.json", "r") as f:
        advice = json.load(f)
    return advice.get("advice", ["No advice available."])

if __name__ == "__main__":
    print(get_advice())