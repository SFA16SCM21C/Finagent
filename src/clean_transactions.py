import pandas as pd
import os

# Category mapping based on personal_finance_category.primary
CATEGORY_MAPPING = {
    'FOOD_AND_DRINK': 'Food',
    'AUTO_AND_TRANSPORT': 'Transportation',
    'BILLS_AND_UTILITIES': 'Bills',
    'SHOPPING': 'Shopping',
    'ENTERTAINMENT': 'Entertainment',
    'TRANSFER': 'Other',
    'PAYMENT': 'Other',
    'INCOME': 'Other'
}

def clean_transactions(input_path="data/transactions.json", output_path="data/transactions_cleaned.json"):
    """Clean and standardize transaction data from JSON."""
    try:
        # Load transactions
        df = pd.read_json(input_path)
        print("Loaded transactions for cleaning.")

        # Select relevant columns
        columns = ['transaction_id', 'date', 'merchant_name', 'name', 'amount', 'personal_finance_category', 'category', 'account_id']
        df = df[columns]

        # Drop rows missing critical fields
        df = df.dropna(subset=['amount'])

        # Fill missing merchant_name with name or "Unknown"
        df['merchant_name'] = df['merchant_name'].fillna(df['name']).fillna('Unknown')

        # Extract primary category from personal_finance_category or fall back to category
        def get_category(row):
            if isinstance(row['personal_finance_category'], dict) and 'primary' in row['personal_finance_category']:
                return row['personal_finance_category']['primary']
            if isinstance(row['category'], list) and row['category']:
                return row['category'][0]
            return 'Uncategorized'
        df['primary_category'] = df.apply(get_category, axis=1)

        # Map to simplified categories
        df['category'] = df['primary_category'].map(CATEGORY_MAPPING).fillna('Uncategorized')

        # Convert date to datetime, coerce invalid dates to NaT
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Drop rows with invalid dates (NaT)
        df = df.dropna(subset=['date'])

        # Clean merchant names (lowercase, remove numbers)
        df['merchant_name'] = df['merchant_name'].str.lower().str.replace(r'\d+', '', regex=True).str.strip()

        # Remove duplicates based on transaction_id
        df = df.drop_duplicates(subset=['transaction_id'])

        # Select final columns
        final_columns = ['transaction_id', 'date', 'merchant_name', 'amount', 'category', 'account_id']
        df = df[final_columns]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save cleaned data
        df.to_json(output_path, orient='records', indent=2, date_format='iso')
        print(f"Cleaned transactions saved to {output_path}")

        return df

    except Exception as e:
        print(f"Error cleaning transactions: {e}")
        return pd.DataFrame()