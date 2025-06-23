# src/advisor.py
from transformers import pipeline
import sqlite3
import pandas as pd
import json
import numpy as np
import os

try:
    advisor = pipeline("text-generation", model="gpt2", framework="pt", device="cpu", truncation=True)
except Exception as e:
    print(f"Failed to initialize pipeline: {e}. Please ensure PyTorch and NumPy are installed.")
    raise

def generate_advice(spending_data, risks):
    """Generate financial advice based on spending data and risks."""
    prompt = (
        f"You are a financial advisor. Based on the following spending data: Needs={spending_data['Needs']}, "
        f"Wants={spending_data['Wants']}, Savings/Debt={spending_data['Savings/Debt']}, and risks: {risks}, "
        f"provide a concise and actionable financial plan."
    )
    response = advisor(prompt, max_length=150, num_return_sequences=1, temperature=0.7)[0]['generated_text']
    return response.strip()

def get_advice(month="2025-06"):
    """Fetch advice for a specific month from database."""
    # Use absolute path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "finagent.db")
    conn = sqlite3.connect(db_path)
    report = pd.read_sql_query(f"SELECT * FROM monthly_reports WHERE month = '{month}'", conn)
    conn.close()
    if not report.empty:
        spending = {
            "Needs": float(report.iloc[0]['needs_amount']),
            "Wants": float(report.iloc[0]['wants_amount']),
            "Savings/Debt": float(report.iloc[0]['savings_debt_amount'])
        }
        risks = report.iloc[0]['risks']
        return generate_advice(spending, risks)
    return "No data available for advice."

def get_rule_based_advice():
    """Fetch legacy rule-based advice as a fallback."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    advice_path = os.path.join(base_dir, "data", "advice_log.json")
    with open(advice_path, "r") as f:
        advice = json.load(f)
    return advice.get("advice", ["No advice available."])

if __name__ == "__main__":
    print(get_advice())