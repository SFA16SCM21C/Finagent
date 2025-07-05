# src/sample_data.py
import json
import random
from datetime import datetime, timedelta
import os
from src.clean_transactions import (
    CATEGORY_MAPPING,
)  # Import category mapping from clean_transactions.py


def generate_sample_transactions(count=600):
    """Generate 500-600 sample transactions for a Lufthansa project manager (2024-2025)."""
    transactions = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days

    # Simulate €4000 monthly income (weekly payments)
    income_weeks = [start_date + timedelta(days=i * 7) for i in range(total_days // 7)]
    income_amount = 4000.0 / 4.33  # Approx weekly income (€4000 / 4.33 weeks/month)

    for i in range(count):
        # Random date within the range
        date = start_date + timedelta(days=random.randint(0, total_days))
        authorized_date = date.strftime(
            "%Y-%m-%d"
        )  # Using ISO format for simplicity and compatibility

        # Define category probabilities based on Lufthansa project manager lifestyle
        category_weights = {
            "TRAVEL": 0.30,  # Frequent airline travel
            "FOOD_AND_DRINK": 0.20,  # Coffee and meals
            "SHOPPING": 0.15,  # Shopping
            "TRANSFER": 0.10,  # Rent
            "LOAN_PAYMENTS": 0.10,  # Credit payments
            "TRANSPORTATION": 0.10,  # Local transport
            "INCOME": 0.04,  # Weekly income
            "ENTERTAINMENT": 0.01,  # Occasional entertainment
        }
        category_key = random.choices(
            list(category_weights.keys()), weights=category_weights.values(), k=1
        )[0]

        # Amount generation
        if category_key == "INCOME":
            amount = income_amount  # Weekly income
        elif category_key == "LOAN_PAYMENTS":
            amount = random.uniform(100.0, 300.0)  # Loan payments
        else:
            amount = random.uniform(5.0, 200.0)  # General expenses

        # 5% chance of refund for travel/shopping
        if category_key in ["TRAVEL", "SHOPPING"] and random.random() < 0.05:
            amount = -abs(amount) * random.uniform(0.1, 0.5)  # Refund 10-50% of amount

        # Construct transaction mimicking API structure
        transaction = {
            "account_id": f"acc{random.randint(1, 3)}",
            "account_owner": None,
            "amount": round(amount, 2),
            "authorized_date": authorized_date,
            "authorized_datetime": None,
            "category": None,
            "category_id": None,
            "check_number": None,
            "counterparties": [
                {
                    "name": (
                        "Lufthansa"
                        if category_key == "TRAVEL"
                        else f"Merchant_{random.randint(1, 10)}"
                    ),
                    "type": "merchant",
                    "website": "lufthansa.com" if category_key == "TRAVEL" else None,
                    "logo_url": (
                        "https://lufthansa-logo.com"
                        if category_key == "TRAVEL"
                        else None
                    ),
                    "confidence_level": "VERY_HIGH",
                    "entity_id": f"ent{random.randint(1000, 9999)}",
                    "phone_number": None,
                }
            ],
            "date": date.strftime("%Y-%m-%d"),  # Using ISO format for consistency
            "datetime": None,
            "iso_currency_code": "EUR",
            "location": {
                "address": None,
                "city": None,
                "region": None,
                "postal_code": None,
                "country": None,
                "lat": None,
                "lon": None,
                "store_number": (
                    str(random.randint(1000, 9999))
                    if category_key != "TRAVEL"
                    else None
                ),
            },
            "logo_url": (
                "https://lufthansa-logo.com" if category_key == "TRAVEL" else None
            ),
            "merchant_entity_id": f"mer{random.randint(1000, 9999)}",
            "merchant_name": (
                "Lufthansa"
                if category_key == "TRAVEL"
                else f"Store_{random.randint(1, 10)}"
            ),
            "name": f"Transaction_{random.randint(1, 10)}",
            "payment_channel": (
                "online"
                if category_key in ["SHOPPING", "ENTERTAINMENT"]
                else "in store"
            ),
            "payment_meta": {
                "reference_number": None,
                "ppd_id": None,
                "payee": None,
                "by_order_of": None,
                "payer": None,
                "payment_method": None,
                "payment_processor": None,
                "reason": None,
            },
            "pending": False,
            "pending_transaction_id": None,
            "personal_finance_category": {
                "confidence_level": "VERY_HIGH",
                "detailed": f"{category_key}_DETAILED",
                "primary": category_key,
            },
            "transaction_code": None,
            "transaction_id": f"tx{random.randint(100000, 999999)}",
            "transaction_type": "place",
            "unofficial_currency_code": None,
            "website": "lufthansa.com" if category_key == "TRAVEL" else None,
        }
        transactions.append(transaction)

    # Ensure weekly income is included
    for week_date in income_weeks[
        : int(count * 0.04)
    ]:  # Approx 4% of transactions as income
        transaction = {
            "account_id": f"acc{random.randint(1, 3)}",
            "amount": round(income_amount, 2),
            "authorized_date": week_date.strftime("%Y-%m-%d"),
            "date": week_date.strftime("%Y-%m-%d"),
            "personal_finance_category": {"primary": "INCOME"},
            "transaction_id": f"inc{random.randint(1000, 9999)}",
        }
        transactions.append(transaction)

    # Save to transactions.json
    os.makedirs("data", exist_ok=True)
    with open("data/transactions.json", "w") as f:
        json.dump(transactions, f, indent=2)
    print(
        f"Generated and saved {len(transactions)} sample transactions to data/transactions.json"
    )

    return transactions
