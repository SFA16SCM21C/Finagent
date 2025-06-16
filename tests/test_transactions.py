import unittest
import json
import pandas as pd
from unittest.mock import patch
from src.transactions import fetch_and_save_transactions
from src.clean_transactions import clean_transactions

class TestTransactionFetcher(unittest.TestCase):
    @patch('src.plaid_client.initialize_plaid_client')
    def test_fetch_invalid_access_token(self, mock_client):
        # Mock Plaid client to raise an error
        mock_client.return_value.transactions_sync.side_effect = Exception("Invalid access token")
        transactions = fetch_and_save_transactions(output_path="data/test_transactions.json")
        self.assertEqual(transactions, [], "Should return empty list on API error")

    @patch('src.plaid_client.initialize_plaid_client')
    def test_fetch_valid_transactions(self, mock_client):
        # Mock Plaid client with sample transactions
        mock_response = {'added': [
            {
                'transaction_id': 'tx1',
                'date': '2025-06-15',
                'merchant_name': 'McDonald\'s',
                'amount': 12.0,
                'personal_finance_category': {'primary': 'FOOD_AND_DRINK'},
                'category': ['Food and Drink'],
                'account_id': 'acc1'
            }
        ], 'has_more': False}
        mock_client.return_value.transactions_sync.return_value = mock_response
        transactions = fetch_and_save_transactions(output_path="data/test_transactions.json")
        self.assertTrue(len(transactions) > 0, "Should return non-empty transactions")
        with open("data/test_transactions.json", "r") as f:
            saved_data = json.load(f)
        self.assertEqual(len(saved_data), 1, "Should save one transaction to JSON")

class TestTransactionCleaner(unittest.TestCase):
    def setUp(self):
        # Path to mock data
        self.mock_file = "data/mock_transactions.json"
        self.output_file = "data/test_cleaned.json"

    def test_drop_missing_date(self):
        # Test if transactions with missing date are dropped
        df = clean_transactions(input_path=self.mock_file, output_path=self.output_file)
        tx2 = df[df['transaction_id'] == 'tx2']
        self.assertTrue(tx2.empty, "Should drop transaction with missing date")

    def test_drop_missing_amount(self):
        # Test if transactions with missing amount are dropped
        df = clean_transactions(input_path=self.mock_file, output_path=self.output_file)
        tx3 = df[df['transaction_id'] == 'tx3']
        self.assertTrue(tx3.empty, "Should drop transaction with missing amount")

    def test_remove_duplicates(self):
        # Test if duplicate transaction_ids are removed
        df = clean_transactions(input_path=self.mock_file, output_path=self.output_file)
        tx1 = df[df['transaction_id'] == 'tx1']
        self.assertEqual(len(tx1), 1, "Should remove duplicate transaction_id")

    def test_category_mapping(self):
        # Test if FOOD_AND_DRINK is mapped to Food
        df = clean_transactions(input_path=self.mock_file, output_path=self.output_file)
        tx1 = df[df['transaction_id'] == 'tx1']
        self.assertFalse(tx1.empty, "Transaction tx1 should exist")
        self.assertEqual(tx1['category'].iloc[0], 'Food', "Should map FOOD_AND_DRINK to Food")

    def test_drop_invalid_date(self):
        # Test if transactions with invalid date are dropped
        df = clean_transactions(input_path=self.mock_file, output_path=self.output_file)
        tx5 = df[df['transaction_id'] == 'tx5']
        self.assertTrue(tx5.empty, "Should drop transaction with invalid date")

if __name__ == '__main__':
    unittest.main()