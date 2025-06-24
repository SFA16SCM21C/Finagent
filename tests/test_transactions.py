# tests/test_transactions.py
import unittest
from src.transactions import fetch_and_save_transactions
from src.clean_transactions import clean_transactions

class TestTransactionFetcher(unittest.TestCase):
    def test_fetch_invalid_access_token(self):
        """Test fetching with an invalid access token."""
        with self.assertRaises(Exception):
            fetch_and_save_transactions("invalid_token")

    def test_fetch_valid_transactions(self):
        """Test fetching valid transactions (mocked in CI)."""
        transactions = fetch_and_save_transactions("valid_token")  # Uses CI mock
        self.assertGreater(len(transactions), 0)
        self.assertIn("date", transactions[0])
        self.assertIn("amount", transactions[0])
        self.assertIn("description", transactions[0])  # Should pass with updated mock
        self.assertIn("transaction_id", transactions[0])

class TestTransactionCleaner(unittest.TestCase):
    def test_category_mapping(self):
        """Test category mapping functionality."""
        data = [{"date": "2025-06-01", "amount": 50, "description": "FOOD_AND_DRINK", "transaction_id": "txn1"}]
        cleaned = clean_transactions(data)
        self.assertEqual(cleaned[0]["category"], "Food")

    def test_drop_invalid_date(self):
        """Test dropping transactions with invalid dates."""
        data = [{"date": "invalid", "amount": 50, "description": "Grocery", "transaction_id": "txn1"}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_amount(self):
        """Test dropping transactions with missing amounts."""
        data = [{"date": "2025-06-01", "description": "Grocery", "transaction_id": "txn1"}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_date(self):
        """Test dropping transactions with missing dates."""
        data = [{"amount": 50, "description": "Grocery", "transaction_id": "txn1"}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_remove_duplicates(self):
        """Test removing duplicate transactions."""
        data = [
            {"date": "2025-06-01", "amount": 50, "description": "Grocery", "transaction_id": "txn1"},
            {"date": "2025-06-01", "amount": 50, "description": "Grocery", "transaction_id": "txn2"}
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)  # Expects one unique transaction based on transaction_id

if __name__ == "__main__":
    unittest.main()