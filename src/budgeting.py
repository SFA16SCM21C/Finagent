# src/budgeting.py
import pandas as pd
import json
import os
from datetime import datetime


def estimate_income(raw_input_path="data/transactions.json", month=None):
    """Estimate monthly income from raw transaction data."""
    try:
        df = pd.read_json(raw_input_path)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "amount"])

        if month is None:
            month = df["date"].dt.to_period("M").max()
        df_month = df[df["date"].dt.to_period("M") == month]

        income_df = df_month[
            (df_month["amount"] < 0)  # Negative amounts indicate income
            & (
                df_month["personal_finance_category"].apply(
                    lambda x: isinstance(x, dict) and x.get("primary") == "INCOME"
                )
                | df_month["merchant_name"].str.contains(
                    "Payroll|Direct Deposit", case=False, na=False
                )
                | df_month["name"].str.contains(
                    "Payroll|Direct Deposit", case=False, na=False
                )
            )
        ]

        income = -income_df[
            "amount"
        ].sum()  # Sum of negative amounts as positive income
        return income if income > 0 else None
    except Exception as e:
        print(f"Error estimating income: {e}")
        return None


def apply_50_30_20_rule(
    clean_input_path="data/transactions_cleaned.json",
    output_path="data/budget_report.json",
    default_income=4000.0,
    custom_savings_goal=None,
):
    """Apply 50/30/20 budgeting rule to transactions and generate a report for each month."""
    try:
        # Load cleaned transactions
        df = pd.read_json(clean_input_path)
        print("Generating budget report for all months...")

        # Convert date to datetime and extract unique months
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        unique_months = df["date"].dt.to_period("M").unique()

        reports = {}

        for month in unique_months:
            month_str = month.strftime("%Y-%m")
            df_month = df[df["date"].dt.to_period("M") == month]

            # Estimate income for the month
            estimated_income = estimate_income("data/transactions.json", month)
            income = (
                estimated_income
                if estimated_income and estimated_income >= 100.0
                else default_income
            )
            income_source = (
                "estimated"
                if income == estimated_income and estimated_income >= 100.0
                else "default"
            )

            # Define category mappings
            needs_categories = ["Bills", "Transportation", "Food"]
            wants_categories = ["Shopping", "Entertainment", "Travel"]
            savings_debt_categories = ["Other"]

            # Allocate spending
            needs_spending = df_month[
                df_month["category"].isin(needs_categories) & (df_month["amount"] > 0)
            ]["amount"].sum()
            wants_spending = df_month[
                df_month["category"].isin(wants_categories) & (df_month["amount"] > 0)
            ]["amount"].sum()
            savings_debt_spending = df_month[
                df_month["category"].isin(savings_debt_categories)
                & (df_month["amount"] > 0)
            ]["amount"].sum()

            # Calculate percentages
            needs_percentage = (needs_spending / income) * 100 if income > 0 else 0
            wants_percentage = (wants_spending / income) * 100 if income > 0 else 0
            savings_debt_percentage = (
                (savings_debt_spending / income) * 100 if income > 0 else 0
            )

            # Determine status
            def get_status(actual, target):
                if actual > target:
                    return "Over"
                elif actual < target:
                    return "Under"
                return "Meets"

            # Custom savings goal handling
            if custom_savings_goal is None:
                custom_savings_goal = income * 0.20  # Default to 20% if not set
            savings_status = get_status(savings_debt_spending, custom_savings_goal)

            # Create monthly report
            report = {
                "month": month_str,
                "income": income,
                "income_source": income_source,
                "estimated_income": estimated_income or 0.0,
                "needs": {
                    "amount": needs_spending,
                    "percentage": needs_percentage,
                    "target_percentage": 50.0,
                    "status": get_status(needs_percentage, 50.0),
                },
                "wants": {
                    "amount": wants_spending,
                    "percentage": wants_percentage,
                    "target_percentage": 30.0,
                    "status": get_status(wants_percentage, 30.0),
                },
                "savings_debt": {
                    "amount": savings_debt_spending,
                    "percentage": savings_debt_percentage,
                    "target_percentage": 20.0,
                    "status": savings_status,
                    "custom_goal": custom_savings_goal,
                },
            }

            reports[month_str] = report
            print(f"Budget Report for {month_str}:")
            print(f"Income: €{income:.2f}")
            print(
                f"Needs: €{needs_spending:.2f} ({needs_percentage:.1f}%, {report['needs']['status'].lower()} 50%)"
            )
            print(
                f"Wants: €{wants_spending:.2f} ({wants_percentage:.1f}%, {report['wants']['status'].lower()} 30%)"
            )
            print(
                f"Savings/Debt: €{savings_debt_spending:.2f} ({savings_debt_percentage:.1f}%, {report['savings_debt']['status'].lower()} 20%, Goal: €{custom_savings_goal:.2f})"
            )

        # Save all reports
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(reports, f, indent=2)
        print(f"Budget reports saved to {output_path}")

        return reports

    except Exception as e:
        print(f"Error generating budget report: {e}")
        return {}
