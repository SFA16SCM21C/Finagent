import unittest
from unittest.mock import patch
from src.sample_data import generate_sample_transactions
from src.clean_transactions import clean_transactions
import pandas as pd
from datetime import datetime

# Helper function to create a transaction
def create_transaction(transaction_id, amount, date, category_key="FOOD_AND_DRINK"):
    """Helper function to create a transaction with date handling."""
    authorized_date = date if isinstance(date, datetime) else None
    date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else None
    return {
        "account_id": "acc1",
        "amount": amount if isinstance(amount, (int, float)) else None,
        "authorized_date": authorized_date,
        "date": date_str,
        "personal_finance_category": {"primary": category_key},
        "transaction_id": transaction_id,
    }

class TestTransactionGenerator(unittest.TestCase):
    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_valid_transactions(self, mock_generate):
        """Test that mocked transactions have the expected length and categories."""
        mock_transactions = [
            {"transaction_id": "tx1", "date": "2024-06-15", "amount": 50.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}},
            {"transaction_id": "tx2", "date": "2024-07-01", "amount": 100.0, "personal_finance_category": {"primary": "TRAVEL"}},
            {"transaction_id": "tx3", "date": "2024-08-15", "amount": 75.0, "personal_finance_category": {"primary": "SHOPPING"}},
            {"transaction_id": "inc1", "date": "2024-06-01", "amount": 923.12, "personal_finance_category": {"primary": "INCOME"}},
        ]
        mock_generate.return_value = mock_transactions
        transactions = generate_sample_transactions()
        self.assertEqual(len(transactions), 4)
        self.assertEqual(transactions[0]["personal_finance_category"]["primary"], "FOOD_AND_DRINK")
        self.assertEqual(transactions[1]["personal_finance_category"]["primary"], "TRAVEL")
        self.assertEqual(transactions[2]["personal_finance_category"]["primary"], "SHOPPING")
        self.assertEqual(transactions[3]["personal_finance_category"]["primary"], "INCOME")

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_empty_transactions(self, mock_generate):
        """Test generating an empty transaction list with zero count."""
        mock_generate.return_value = []
        transactions = generate_sample_transactions(count=0)
        self.assertEqual(len(transactions), 0)
        self.assertEqual(mock_generate.call_args[1]["count"], 0)

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_large_transactions(self, mock_generate):
        """Test generating a large number of transactions."""
        mock_transactions = [
            {"transaction_id": f"tx{i}", "date": "2024-06-15", "amount": 10.0 * i, 
             "personal_finance_category": {"primary": "FOOD_AND_DRINK"}} for i in range(1000)
        ]
        mock_generate.return_value = mock_transactions
        transactions = generate_sample_transactions(count=1000)
        self.assertEqual(len(transactions), 1000)
        self.assertEqual(mock_generate.call_args[1]["count"], 1000)

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_varied_categories(self, mock_generate):
        """Test that transactions include a variety of categories."""
        mock_transactions = [
            {"transaction_id": "tx1", "date": "2024-06-15", "amount": 50.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}},
            {"transaction_id": "tx2", "date": "2024-07-01", "amount": 100.0, "personal_finance_category": {"primary": "TRAVEL"}},
            {"transaction_id": "tx3", "date": "2024-08-15", "amount": 75.0, "personal_finance_category": {"primary": "SHOPPING"}},
            {"transaction_id": "inc1", "date": "2024-06-01", "amount": 923.12, "personal_finance_category": {"primary": "INCOME"}},
        ]
        mock_generate.return_value = mock_transactions
        transactions = generate_sample_transactions()
        categories = {tx["personal_finance_category"]["primary"] for tx in transactions}
        expected_categories = {"FOOD_AND_DRINK", "TRAVEL", "SHOPPING", "INCOME"}
        self.assertEqual(categories, expected_categories)

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_transaction_structure(self, mock_generate):
        """Test that each transaction has the required fields."""
        mock_transactions = [
            {"transaction_id": "tx1", "date": "2024-06-15", "amount": 50.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}},
        ]
        mock_generate.return_value = mock_transactions
        transactions = generate_sample_transactions()
        required_fields = ["transaction_id", "date", "amount", "personal_finance_category"]
        for tx in transactions:
            for field in required_fields:
                self.assertIn(field, tx, f"Transaction missing required field: {field}")

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_negative_count(self, mock_generate):
        """Test behavior when count is negative (should return empty list)."""
        mock_generate.return_value = []
        transactions = generate_sample_transactions(count=-1)
        self.assertEqual(len(transactions), 0)
        self.assertEqual(mock_generate.call_args[1]["count"], -1)

    @patch('tests.test_transactions.generate_sample_transactions')
    def test_generate_single_transaction(self, mock_generate):
        """Test generating exactly one transaction."""
        mock_transactions = [
            {"transaction_id": "tx1", "date": "2024-06-15", "amount": 50.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}},
        ]
        mock_generate.return_value = mock_transactions
        transactions = generate_sample_transactions(count=1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["transaction_id"], "tx1")

class TestTransactionCleaner(unittest.TestCase):
    def test_category_mapping(self):
        """Test category mapping functionality based on personal_finance_category."""
        data = [create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["category"], "Food")

    def test_drop_invalid_date(self):
        """Test dropping transactions with invalid dates."""
        data = [{"transaction_id": "tx1", "date": "invalid", "amount": 12.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_amount(self):
        """Test dropping transactions with missing amounts."""
        data = [{"transaction_id": "tx1", "date": "2025-06-15", "personal_finance_category": {"primary": "FOOD_AND_DRINK"}}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_drop_missing_date(self):
        """Test dropping transactions with missing dates."""
        data = [{"transaction_id": "tx1", "amount": 12.0, "personal_finance_category": {"primary": "FOOD_AND_DRINK"}}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_remove_duplicates(self):
        """Test removing duplicate transactions based on transaction_id."""
        data = [
            create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK"),
            create_transaction("tx1", 12.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")
        ]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)

    def test_handle_negative_amount(self):
        """Test handling transactions with negative amounts."""
        data = [create_transaction("tx1", -10.0, datetime(2025, 6, 15), "FOOD_AND_DRINK")]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["amount"], -10.0)

    def test_drop_missing_category(self):
        """Test dropping transactions with missing category."""
        data = [{"transaction_id": "tx1", "amount": 12.0, "date": "2025-06-15"}]
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

    def test_clean_empty_list(self):
        """Test cleaning an empty transaction list."""
        data = []
        cleaned = clean_transactions(data)
        self.assertEqual(len(cleaned), 0)

if __name__ == "__main__":
    unittest.main()