# src/main.py
import os
from src.sample_data import generate_sample_transactions
from src.clean_transactions import clean_transactions

# from src.transactions import fetch_and_save_transactions  # Commented out as a learning step
from src.budgeting import apply_50_30_20_rule  # Will be used later
from src.analysis import analyze_spending  # Will be used later

# from src.advisor_old import generate_advice_and_qa  # Will be used later


def main():
    """Main function to run the FinAgent transaction pipeline."""
    print("Starting FinAgent transaction pipeline...")
    # Commenting out API call as a learning step; static API limits data variety
    # transactions = fetch_and_save_transactions(os.getenv("PLAID_ACCESS_TOKEN", "access-sandbox-9edbddce-23cc-4f2e-8614-2cfea6713146"))
    # print(f"Fetched transactions: {transactions}")
    # if transactions:
    #     print("Cleaning transactions...")
    #     cleaned_df = clean_transactions(transactions)
    # Instead, we'll use a static sample dataset for demonstration with 500-600 transactions
    sample_transactions = generate_sample_transactions(
        600
    )  # Generate and save 600 transactions
    print(f"Generated {len(sample_transactions)} sample transactions")
    print("Cleaning transactions...")
    cleaned_df = clean_transactions(sample_transactions)
    print("Generating budget reports...")
    budget_reports = apply_50_30_20_rule()
    print("Analyzing spending...")
    analysis_reports = analyze_spending(budget_reports["2025-06"]["income"])
    # Further processing (dashboard, etc.) to be added in subsequent steps
    print(
        "Pipeline completed (initial setup with sample data, cleaning, budgeting, and analysis)."
    )


if __name__ == "__main__":
    main()
