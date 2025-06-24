# tests/test_transactions.py
import unittest
import os
from src.transactions import fetch_and_save_transactions
from src.clean_transactions import clean_transactions

class TestTransactionFetcher(unittest.TestCase):
    def test_fetch_invalid_access_token(self):
        """Test fetching with an invalid access token."""
        with self.assertRaises(Exception):
            fetch_and_save_transactions("invalid_token")

    def test_fetch_valid_transactions(self):
        """Test fetching valid transactions (mocked in CI)."""
        transactions = fetch_and_save_transactions(os.getenv("PLAID_ACCESS_TOKEN"))
        self.assertGreater(len(transactions), 0)
        self.assertIn("date", transactions[0])
        self.assertIn("amount", transactions[0])
        self.assertIn("personal_finance_category", transactions[0])
        self.assertIn("transaction_id", transactions[0])

class TestTransactionCleaner(unittest.TestCase):
    def test_category_mapping(self):
        """Test category mapping functionality based on personal_finance_category."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "amount": 12.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Food")

    def test_drop_invalid_date(self):
        """Test dropping transactions with invalid dates."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "invalid",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "amount": 12.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_amount(self):
        """Test dropping transactions with missing amounts."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_date(self):
        """Test dropping transactions with missing dates."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "amount": 12.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_remove_duplicates(self):
        """Test removing duplicate transactions based on transaction_id."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "amount": 12.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            },
            {
                "transaction_id": "tx1",  # Duplicate transaction_id
                "account_id": "acc2",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's #3322",
                "amount": 12.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)

if __name__ == "__main__":
    unittest.main()