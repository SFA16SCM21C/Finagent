import pandas as pd
import sqlite3
import json
import os
import re

def generate_advice_and_qa(db_path="data/finagent.db", transactions_path="data/transactions_cleaned.json", output_path="data/advice_log.json"):
    """Generate financial advice and answer queries using SQLite reports and transactions."""
    try:
        print("Generating advice...")

        # Connect to SQLite
        conn = sqlite3.connect(db_path)
        report_df = pd.read_sql_query("SELECT * FROM monthly_reports WHERE month = '2025-06'", conn)
        conn.close()

        # Get latest report
        if report_df.empty:
            print("No reports found in database for 2025-06.")
            return {}
        report = report_df.iloc[0].to_dict()

        # Generate advice based on risks
        advice = []
        risks = report['risks']
        income = report['income']

        if "Low Savings/Debt" in risks:
            advice.append(f"Increase debt payments by ${income*0.025:.2f}/month to reduce interest costs.")
        if "High Wants" in risks:
            advice.append(f"Reduce Wants spending by ${report['wants_amount']*0.4:.2f} to align with 30% target.")

        # Load transactions for Q&A
        df = pd.read_json(transactions_path)
        df['date'] = pd.to_datetime(df['date'])

        # Hardcoded queries for testing
        queries = [
            "How much on Food in June 2025?",
            "What’s my budget status for June 2025?"
        ]
        qa_responses = []

        for query in queries:
            # Parse query
            category_match = re.search(r'\bon\s+(\w+)', query, re.IGNORECASE)
            is_budget_status = "budget status" in query.lower()

            if is_budget_status:
                answer = (
                    f"Needs: {(report['needs_amount']/income*100):.1f}% (under 50%), "
                    f"Wants: {(report['wants_amount']/income*100):.1f}% (under 30%), "
                    f"Savings/Debt: {(report['savings_debt_amount']/income*100):.1f}% (under 20%). "
                    f"Risk: {risks if risks != 'None' else 'None'}."
                )
                qa_responses.append({"query": query, "answer": answer})
            elif category_match:
                category = category_match.group(1).capitalize()
                df_query = df[
                    (df['category'] == category) &
                    (df['date'].dt.year == 2025) &
                    (df['date'].dt.month == 6)
                ]
                total = df_query[df_query['amount'] > 0]['amount'].sum()
                answer = f"You spent ${total:.2f} on {category} in June 2025."
                qa_responses.append({"query": query, "answer": answer})

        # Validate responses
        for qa in qa_responses:
            if "Food" in qa['query'] and abs(float(qa['answer'].split('$')[1].split(' ')[0]) - 16.33) > 0.01:
                print(f"Warning: Food spending answer ({qa['answer']}) does not match expected $16.33.")

        # Print results
        print("Advice:")
        for a in advice:
            print(f"- {a}")
        if not advice:
            print("- None")
        print("Q&A Responses:")
        for qa in qa_responses:
            print(f"- Query: {qa['query']}\n  Answer: {qa['answer']}")

        # Save log
        #testing CI/CD run
        log = {
            "month": report['month'],
            "advice": advice,
            "qa_responses": qa_responses
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(log, f, indent=2)
        print(f"Advice log saved to {output_path}")

        return log

    except Exception as e:
        print(f"Error generating advice: {e}")
        return {}