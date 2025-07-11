# src/main.py
import os
from src.sample_data import generate_sample_transactions
from src.clean_transactions import clean_transactions
from src.budgeting import apply_50_30_20_rule  # Will be used later
from src.analysis import analyze_spending  # Will be used later


def main():
    """Main function to run the FinAgent transaction pipeline."""
    print("Starting FinAgent transaction pipeline...")
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
