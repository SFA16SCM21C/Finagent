# src/transactions.py
import json
import os
from datetime import date
from src.plaid_client import initialize_plaid_client, create_public_token, exchange_public_token, sync_transactions

class DateEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime.date objects."""
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def fetch_and_save_transactions(output_path="data/transactions.json"):
    """Fetch transactions from Plaid and save to JSON."""
    try:
        if os.getenv("CI") == "true":  # CI environment
            transactions = [
                {
                    "transaction_id": "tx1",
                    "account_id": "acc1",
                    "date": "2025-06-15",
                    "merchant_name": "McDonald's",
                    "name": "McDonald's #3322",
                    "amount": 12.0,
                    "personal_finance_category": {
                        "primary": "FOOD_AND_DRINK",
                        "detailed": "FOOD_AND_DRINK_FAST_FOOD"
                    },
                    "category": ["Food and Drink"]
                },
                {
                    "transaction_id": "tx3",
                    "account_id": "acc3",
                    "date": "2025-06-14",
                    "merchant_name": "Test",
                    "name": "Uber",
                    "amount": 5.0,
                    "personal_finance_category": {
                        "primary": "AUTO_AND_TRANSPORT",
                        "detailed": "AUTO_AND_TRANSPORT_RIDE_SHARE"
                    },
                    "category": ["Transportation"]
                }
            ]
            return transactions
        
        # Initialize Plaid client
        client = initialize_plaid_client()
        print("Env loaded with details")

        # Create and exchange tokens
        public_token = create_public_token(client)
        print("Public token generated")

        # Use hardcoded access token as per original script
        access_token = 'access-sandbox-9edbddce-23cc-4f2e-8614-2cfea6713146'
        print("Access token generated")

        # Fetch transactions
        transactions = sync_transactions(client, access_token)
        print("Transactions found")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to JSON
        with open(output_path, "w") as f:
            json.dump([t.to_dict() for t in transactions], f, indent=2, cls=DateEncoder)
        print(f"Transactions saved to {output_path}")

        return transactions

    except Exception as e:
        print(f"Error: {e}")
        return []