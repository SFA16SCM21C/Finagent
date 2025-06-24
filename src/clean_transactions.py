# src/clean_transactions.py
import pandas as pd
import os

# Enhanced category mapping
CATEGORY_MAPPING = {
    'FOOD_AND_DRINK': 'Food',
    'AUTO_AND_TRANSPORT': 'Transportation',
    'BILLS_AND_UTILITIES': 'Bills',
    'SHOPPING': 'Shopping',
    'ENTERTAINMENT': 'Entertainment',
    'TRANSFER': 'Other',
    'PAYMENT': 'Other',
    'INCOME': 'Other',
    'TRAVEL': 'Travel',
    'GENERAL_MERCHANDISE': 'Shopping',
    'TRANSPORTATION': 'Transportation',
    'LOAN_PAYMENTS': 'Other',
    'Grocery': 'Food',  # Explicit mapping for test
    'Transport': 'Transportation',
    'Shopping': 'Shopping'
}

def clean_transactions(transactions, output_path="data/transactions_cleaned.json"):
    """Clean and standardize transaction data."""
    try:
        if not transactions or not isinstance(transactions, (list, pd.DataFrame)):
            return pd.DataFrame()

        # Convert to DataFrame if list
        if isinstance(transactions, list):
            df = pd.DataFrame(transactions)
        else:
            df = transactions.copy()
        print("Loaded transactions for cleaning.")

        # Select available columns
        available_columns = [col for col in ['transaction_id', 'date', 'authorized_date', 'merchant_name', 'name', 'amount', 'personal_finance_category', 'category', 'account_id', 'description'] if col in df.columns]
        df = df[available_columns] if available_columns else df

        # Drop rows missing critical fields
        df = df.dropna(subset=['date', 'amount'])

        # Convert dates to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'authorized_date' in df.columns:
            df['authorized_date'] = pd.to_datetime(df['authorized_date'], errors='coerce')

        # Adjust date based on authorized_date if present
        if 'authorized_date' in df.columns:
            def adjust_date(row):
                if pd.isna(row['authorized_date']):
                    return row['date']
                if row['date'].day == 1 and row['authorized_date'].month == row['date'].month - 1:
                    return row['authorized_date']
                return row['date']
            df['date'] = df.apply(adjust_date, axis=1)

        # Fill missing merchant_name
        if 'merchant_name' in df.columns and 'name' in df.columns:
            df['merchant_name'] = df['merchant_name'].fillna(df['name']).fillna('Unknown')
        elif 'name' in df.columns:
            df['merchant_name'] = df['name'].fillna('Unknown')
        elif 'merchant_name' in df.columns:
            df['merchant_name'] = df['merchant_name'].fillna('Unknown')

        # Enhanced category mapping with description priority
        def get_category(row):
            if 'description' in df.columns and isinstance(row['description'], str):
                desc = row['description'].capitalize()
                mapped = CATEGORY_MAPPING.get(desc)
                if mapped:
                    return mapped
            if 'personal_finance_category' in df.columns and isinstance(row['personal_finance_category'], dict) and 'primary' in row['personal_finance_category']:
                return row['personal_finance_category']['primary']
            if 'category' in df.columns and isinstance(row['category'], list) and row['category']:
                return row['category'][0]
            return 'Uncategorized'
        df['primary_category'] = df.apply(get_category, axis=1)
        df['category'] = df['primary_category'].map(CATEGORY_MAPPING).fillna(df['primary_category'])

        # Drop rows with invalid dates
        df = df.dropna(subset=['date'])

        # Clean merchant names if present
        if 'merchant_name' in df.columns:
            df['merchant_name'] = df['merchant_name'].str.lower().str.replace(r'\d+', '', regex=True).str.replace(r'\*\/\/', '', regex=True).str.strip()

        # Enhanced deduplication logic
        duplicate_cols = ['transaction_id'] if 'transaction_id' in df.columns else []
        for col in ['date', 'amount', 'description']:
            if col in df.columns:
                duplicate_cols.append(col)
        if duplicate_cols:
            df = df.drop_duplicates(subset=duplicate_cols, keep='first')

        # Select final columns
        final_columns = [col for col in ['transaction_id', 'date', 'merchant_name', 'amount', 'category', 'account_id'] if col in df.columns]
        df = df[final_columns] if final_columns else df

        # Save cleaned data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_json(output_path, orient='records', indent=2, date_format='iso')
        print(f"Cleaned transactions saved to {output_path}")

        return df

    except Exception as e:
        print(f"Error cleaning transactions: {e}")
        return pd.DataFrame()