# src/main.py
import os
from src.transactions import fetch_and_save_transactions
from src.clean_transactions import clean_transactions
from src.budgeting import apply_50_30_20_rule
from src.analysis import analyze_spending
from src.advisor_old import generate_advice_and_qa

def main():
    """Main function to run the FinAgent transaction pipeline."""
    print("Starting FinAgent transaction pipeline...")
    # Use environment variable or default for local testing
    access_token = os.getenv("PLAID_ACCESS_TOKEN", "access-sandbox-9edbddce-23cc-4f2e-8614-2cfea6713146")
    transactions = fetch_and_save_transactions(access_token)
    print(f"Fetched transactions: {transactions}")  # Debug print
    if transactions:
        print("Cleaning transactions...")
        cleaned_df = clean_transactions(transactions)
        print(f"Cleaned DataFrame columns: {cleaned_df.columns.tolist()}")  # Debug print
        if not cleaned_df.empty:
            print("Generating budget report...")
            budget_report = apply_50_30_20_rule()  # Uses saved file
            if budget_report:
                print("Analyzing spending...")
                analysis_report = analyze_spending(income=budget_report['income'])
                if analysis_report:
                    print("Generating advice...")
                    advice_log = generate_advice_and_qa(analysis_report)
    print("Pipeline completed.")

if __name__ == "__main__":
    main()