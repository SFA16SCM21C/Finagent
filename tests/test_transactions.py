import unittest
from unittest.mock import patch, mock_open
from src.sample_data import generate_transactions  # Adjusted import
from src.transactions import fetch_and_save_transactions
from src.clean_transactions import clean_transactions
import pandas as pd
from datetime import datetime
import random

def create_transaction(transaction_id, amount, date, category_key="FOOD_AND_DRINK"):
    """Helper function to create a transaction based on the provided JSON structure."""
    authorized_date = date
    return {
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
                "name": "Lufthansa" if category_key == "TRAVEL" else f"Merchant_{random.randint(1, 10)}",
                "type": "merchant",
                "website": "lufthansa.com" if category_key == "TRAVEL" else None,
                "logo_url": "https://lufthansa-logo.com" if category_key == "TRAVEL" else None,
                "confidence_level": "VERY_HIGH",
                "entity_id": f"ent{random.randint(1000, 9999)}",
                "phone_number": None
            }
        ],
        "date": date.strftime("%Y-%m-%d"),
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
            "store_number": str(random.randint(1000, 9999)) if category_key != "TRAVEL" else None
        },
        "logo_url": "https://lufthansa-logo.com" if category_key == "TRAVEL" else None,
        "merchant_entity_id": f"mer{random.randint(1000, 9999)}",
        "merchant_name": "Lufthansa" if category_key == "TRAVEL" else f"Store_{random.randint(1, 10)}",
        "name": f"Transaction_{random.randint(1, 10)}",
        "payment_channel": "online" if category_key in ["SHOPPING", "ENTERTAINMENT"] else "in store",
        "payment_meta": {
            "reference_number": None,
            "ppd_id": None,
            "payee": None,
            "by_order_of": None,
            "payer": None,
            "payment_method": None,
            "payment_processor": None,
            "reason": None
        },
        "pending": False,
        "pending_transaction_id": None,
        "personal_finance_category": {
            "confidence_level": "VERY_HIGH",
            "detailed": f"{category_key}_DETAILED",
            "primary": category_key
        },
        "transaction_code": None,
        "transaction_id": transaction_id,
        "transaction_type": "place",
        "unofficial_currency_code": None,
        "website": "lufthansa.com" if category_key == "TRAVEL" else None
    }

class TestTransactionFetcher(unittest.TestCase):
    def test_fetch_invalid_access_token(self):
        """Test fetching with an invalid access token (now a placeholder)."""
        with self.assertRaises(ValueError):  # Adjusted to ValueError as a placeholder
            fetch_and_save_transactions(None)  # Assuming no token needed with generate_transactions

    def test_fetch_valid_transactions(self):
        """Test fetching valid transactions using generate_transactions."""
        with patch("src.sample_data.generate_transactions") as mock_generate:
            mock_generate.return_value = [
                create_transaction("tx1", 50.0, datetime(2025, 6, 15))
            ]
            transactions = fetch_and_save_transactions()
            self.assertGreater(len(transactions), 0)
            self.assertIn("date", transactions[0])
            self.assertIn("amount", transactions[0])
            self.assertIn("personal_finance_category", transactions[0])
            self.assertIn("transaction_id", transactions[0])

    def test_fetch_empty_transactions(self):
        """Test fetching an empty transaction list."""
        with patch("src.sample_data.generate_transactions") as mock_generate:
            mock_generate.return_value = []
            transactions = fetch_and_save_transactions()
            self.assertEqual(len(transactions), 0)

    def test_fetch_file_permission_error(self):
        """Test fetching with file permission error."""
        with patch("src.sample_data.generate_transactions") as mock_generate:
            mock_generate.return_value = [create_transaction("tx1", 50.0, datetime(2025, 6, 15))]
            with patch("builtins.open", mock_open()) as mock_file:
                mock_file.side_effect = PermissionError
                with self.assertRaises(PermissionError):
                    fetch_and_save_transactions()

class TestTransactionCleaner(unittest.TestCase):
    def test_category_mapping(self):
        """Test category mapping functionality based on personal_finance_category."""
        from datetime import datetime
        data = [create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Food")

    def test_drop_invalid_date(self):
        """Test dropping transactions with invalid dates."""
        data = [create_transaction("tx1", 12.0, "invalid", "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_amount(self):
        """Test dropping transactions with missing amounts."""
        data = [{"transaction_id": "tx1", "date": "2025-06-15", "personal_finance_category": {"primary": "FOOD_AND_DRINK"}}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_date(self):
        """Test dropping transactions with missing dates."""
        data = [create_transaction("tx1", 12.0, None, "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_remove_duplicates(self):
        """Test removing duplicate transactions based on transaction_id."""
        from datetime import datetime
        data = [
            create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK"),
            create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)

    def test_missing_personal_finance_category(self):
        """Test handling transactions without personal_finance_category."""
        data = [{"transaction_id": "tx1", "date": "2025-06-15", "amount": 30.0, "category": ["SHOPPING"]}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Shopping")

    def test_multiple_categories(self):
        """Test extracting primary category from multiple category entries."""
        from datetime import datetime
        data = [create_transaction("tx1", 200.0, datetime(2025, 6, 15), "TRAVEL")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Travel")

    def test_negative_amount(self):
        """Test handling negative amounts (e.g., refunds)."""
        from datetime import datetime
        data = [create_transaction("tx1", -10.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["amount"], -10.0)

    # New Test Cases
    def test_empty_transaction_list(self):
        """Test handling an empty transaction list."""
        data = []
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_invalid_amount_type(self):
        """Test handling non-numeric amount values."""
        data = [{"transaction_id": "tx1", "date": "2025-06-15", "amount": "invalid", "personal_finance_category": {"primary": "FOOD_AND_DRINK"}}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_boundary_amounts(self):
        """Test handling minimum and maximum amount boundaries."""
        from datetime import datetime
        data = [
            create_transaction("tx1", -1000.0, datetime(2025, 6, 15), "FOOD_AND_DRINK"),
            create_transaction("tx2", 10000.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.iloc[0]["amount"], -1000.0)
        self.assertEqual(cleaned.iloc[1]["amount"], 10000.0)

    def test_invalid_personal_finance_category(self):
        """Test handling invalid personal_finance_category values."""
        from datetime import datetime
        data = [create_transaction("tx1", 25.0, datetime(2025, 6, 15), "INVALID_CATEGORY")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Other")

    def test_large_transaction_dataset(self):
        """Test handling a large dataset of transactions."""
        from datetime import datetime
        data = [create_transaction(f"tx{i}", 10.0, datetime(2025, 6, 15), "FOOD_AND_DRINK") for i in range(1000)]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1000)

    def test_file_save_success(self):
        """Test successful file save operation (mocked)."""
        from datetime import datetime
        with patch("src.sample_data.generate_transactions") as mock_generate:
            mock_generate.return_value = [create_transaction("tx1", 50.0, datetime(2025, 6, 15))]
            with patch("builtins.open", mock_open()) as mock_file:
                transactions = fetch_and_save_transactions()
                mock_file.assert_called_with("data/transactions_cleaned.json", "w")
                self.assertGreater(len(transactions), 0)

    def test_nested_counterparty_data(self):
        """Test handling nested counterparty data."""
        from datetime import datetime
        data = [create_transaction("tx1", 100.0, datetime(2025, 6, 15), "TRAVEL")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertIn("counterparties", data[0])
        self.assertEqual(cleaned.iloc[0]["category"], "Travel")

    def test_partial_data(self):
        """Test handling transactions with partial data (e.g., missing nested fields)."""
        from datetime import datetime
        partial_data = {
            "transaction_id": "tx1",
            "date": "2025-06-15",
            "amount": 50.0,
            "personal_finance_category": {"primary": "SHOPPING"}
        }
        cleaned = clean_transactions([partial_data])
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Shopping")

    def test_unexpected_nested_values(self):
        """Test handling unexpected values in nested fields."""
        from datetime import datetime
        data = [
            {
                "transaction_id": "tx1",
                "date": "2025-06-15",
                "amount": 50.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK", "invalid_field": "test"},
                "counterparties": [{"name": "Merchant_1", "invalid_field": "test"}]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Food")

if __name__ == "__main__":
    unittest.main()