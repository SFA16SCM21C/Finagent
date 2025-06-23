import sqlite3
from transformers import pipeline

# Initialize LLM
advisor = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

def generate_advice(spending_data, risks):
    prompt = f"Based on spending data {spending_data} and risks {risks}, suggest a financial plan."
    response = advisor(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
    return response.strip()

# Example usage with existing data
def get_advice():
    conn = sqlite3.connect("data/finagent.db")
    report = pd.read_sql_query("SELECT * FROM monthly_reports WHERE month = '2025-06'", conn)
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