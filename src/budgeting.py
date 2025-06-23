import pandas as pd
import json
import os
from datetime import datetime

def estimate_income(raw_input_path="data/transactions.json", month=None):
    """Estimate monthly income from raw transaction data."""
    try:
        df = pd.read_json(raw_input_path)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date', 'amount'])

        # Filter for specified month or latest month
        if month is None:
            month = df['date'].dt.to_period('M').max()
        df_month = df[df['date'].dt.to_period('M') == month]

        # Identify income transactions
        income_df = df_month[
            (df_month['amount'] < 0) &  # Negative amounts are credits
            (
                df_month['personal_finance_category'].apply(
                    lambda x: isinstance(x, dict) and x.get('primary') == 'INCOME'
                ) |
                df_month['merchant_name'].str.contains('Payroll|Direct Deposit', case=False, na=False) |
                df_month['name'].str.contains('Payroll|Direct Deposit', case=False, na=False)
            )
        ]

        income = -income_df['amount'].sum()  # Convert negative to positive
        return income if income > 0 else None

    except Exception as e:
        print(f"Error estimating income: {e}")
        return None

def apply_50_30_20_rule(clean_input_path="data/transactions_cleaned.json", output_path="data/budget_report.json", default_income=4000.0):
    """Apply 50/30/20 budgeting rule to transactions and generate a report."""
    try:
        # Estimate income from raw transactions
        estimated_income = estimate_income()
        income = estimated_income if estimated_income and estimated_income >= 100.0 else default_income
        income_source = "estimated" if income == estimated_income and estimated_income >= 100.0 else "default"
        print(f"Estimated income: ${income:.2f} ({income_source}, estimated ${estimated_income or 0:.2f} {'too low' if estimated_income else 'not found'})")

        # Load cleaned transactions
        df = pd.read_json(clean_input_path)
        print("Generating budget report...")

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Filter for June 2025 explicitly
        df_month = df[(df['date'].dt.year == 2025) & (df['date'].dt.month == 6)]

        # Define category mappings
        needs_categories = ['Bills', 'Transportation']
        wants_categories = ['Shopping', 'Entertainment', 'Travel']
        savings_debt_categories = ['Other']

        # Allocate Food: 50% to Needs (groceries), 50% to Wants (dining)
        food_df = df_month[df_month['category'] == 'Food']
        food_total = food_df[food_df['amount'] > 0]['amount'].sum()  # Exclude negative amounts
        needs_food = food_total * 0.5
        wants_food = food_total * 0.5

        # Calculate spending by category, excluding negative amounts
        needs_spending = df_month[(df_month['category'].isin(needs_categories)) & (df_month['amount'] > 0)]['amount'].sum() + needs_food
        wants_spending = df_month[(df_month['category'].isin(wants_categories)) & (df_month['amount'] > 0)]['amount'].sum() + wants_food
        savings_debt_spending = df_month[(df_month['category'].isin(savings_debt_categories)) & (df_month['amount'] > 0)]['amount'].sum()

        # Calculate percentages
        needs_percentage = (needs_spending / income) * 100
        wants_percentage = (wants_spending / income) * 100
        savings_debt_percentage = (savings_debt_spending / income) * 100

        # Determine status
        def get_status(actual, target):
            if actual > target:
                return "Over"
            elif actual < target:
                return "Under"
            return "Meets"

        # Create report
        report = {
            "month": "2025-06",
            "income": income,
            "income_source": income_source,
            "estimated_income": estimated_income or 0.0,
            "needs": {
                "amount": needs_spending,
                "percentage": needs_percentage,
                "target_percentage": 50.0,
                "status": get_status(needs_percentage, 50.0)
            },
            "wants": {
                "amount": wants_spending,
                "percentage": wants_percentage,
                "target_percentage": 30.0,
                "status": get_status(wants_percentage, 30.0)
            },
            "savings_debt": {
                "amount": savings_debt_spending,
                "percentage": savings_debt_percentage,
                "target_percentage": 20.0,
                "status": get_status(savings_debt_percentage, 20.0)
            }
        }

        # Print report
        print(f"Budget Report for 2025-06:")
        print(f"Income: ${income:.2f}")
        print(f"Needs: ${needs_spending:.2f} ({needs_percentage:.1f}%, {report['needs']['status'].lower()} 50%)")
        print(f"Wants: ${wants_spending:.2f} ({wants_percentage:.1f}%, {report['wants']['status'].lower()} 30%)")
        print(f"Savings/Debt: ${savings_debt_spending:.2f} ({savings_debt_percentage:.1f}%, {report['savings_debt']['status'].lower()} 20%)")

        # Save report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Budget report saved to {output_path}")

        return report

    except Exception as e:
        print(f"Error generating budget report: {e}")
        return {}