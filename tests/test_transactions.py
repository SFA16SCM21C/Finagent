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

    def test_missing_personal_finance_category(self):
        """Test handling transactions without personal_finance_category."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "Target",
                "name": "Target Purchase",
                "amount": 30.0,
                "category": ["SHOPPING"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Shopping")

    def test_multiple_categories(self):
        """Test extracting primary category from multiple category entries."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "Travel Agency",
                "name": "Travel Booking",
                "amount": 200.0,
                "personal_finance_category": {"primary": "TRAVEL"},
                "category": ["Travel", "Transportation", "Booking"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Travel")

    def test_negative_amount(self):
        """Test handling negative amounts (e.g., refunds)."""
        data = [
            {
                "transaction_id": "tx1",
                "account_id": "acc1",
                "date": "2025-06-15",
                "authorized_date": "2025-06-15",
                "merchant_name": "McDonald's",
                "name": "McDonald's Refund",
                "amount": -10.0,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK"},
                "category": ["Food and Drink"]
            }
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["amount"], -10.0)  # Allow negative amounts

if __name__ == "__main__":
    unittest.main()