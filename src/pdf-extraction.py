import boto3
import json
import re
import os

# AWS client
textract = boto3.client('textract')

def get_tables_from_textract(response):
    """
    Parses Textract response to extract tables, rows, and cell text.
    
    Parameters:
    response (dict): Textract analyze_document response.
    
    Returns:
    list: List of tables, each as list of rows (list of cell texts).
    """
    blocks = response['Blocks']
    tables = []
    current_table = []
    current_row = []
    for block in blocks:
        if block['BlockType'] == 'TABLE':
            # Start new table
            if current_table:
                tables.append(current_table)
            current_table = []
        elif block['BlockType'] == 'CELL':
            row_index = block['RowIndex']
            col_index = block['ColumnIndex']
            if 'Relationships' in block:
                cell_text = ' '.join([get_text_from_block(blocks, rel['Ids'][0]) for rel in block['Relationships'] if rel['Type'] == 'CHILD'])
            else:
                cell_text = ''
            # New row if col_index resets to 1
            if col_index == 1:
                if current_row:
                    current_table.append(current_row)
                current_row = [cell_text]
            else:
                current_row.append(cell_text)
    if current_table:
        tables.append(current_table)
    return tables

def get_text_from_block(blocks, block_id):
    """
    Retrieves text from a block by ID.
    """
    for block in blocks:
        if block['Id'] == block_id and 'Text' in block:
            return block['Text']
    return ''

def parse_transaction(row):
    """
    Parses a table row into transaction dictionary.
    
    Parameters:
    row (list): [description, booking_date, amount]
    
    Returns:
    dict: Transaction data or None if invalid.
    """
    if len(row) != 3:
        return None
    description = row[0].replace('\n', ' ').strip()
    booking_date = row[1].strip()
    amount_str = row[2].strip()
    
    # Parse description
    parts = re.split(r'\s{2,}', description)  # Split on multiple spaces for multi-part
    if not parts:
        return None
    merchant = parts[0]
    remaining = parts[1:]
    
    category = ""
    additional_details = []
    value_date = None
    value_date_pattern = re.compile(r'Fecha de valor (\d{2}\.\d{2}\.\d{4})')
    
    for part in remaining:
        match = value_date_pattern.search(part)
        if match:
            value_date = match.group(1)
        elif 'Mastercard •' in part:
            category = part.replace(' • ', ' ')
        else:
            additional_details.append(part)
    
    if not value_date or not booking_date or not amount_str:
        return None
    
    # Parse amount
    amount_clean = amount_str.replace('€', '').replace('.', '').replace(',', '.').strip()
    amount = float(amount_clean)
    
    # Convert dates
    def convert_date(date_str):
        day, month, year = date_str.split('.')
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    return {
        "merchant_or_person": merchant,
        "category_or_type": category,
        "additional_details": ' '.join(additional_details).replace(' • ', ' '),
        "value_date": convert_date(value_date),
        "booking_date": convert_date(booking_date),
        "amount": amount
    }

def extract_transactions(pdf_path):
    """
    Extracts transactions from PDF using Textract and parses into JSON format.
    
    Parameters:
    pdf_path (str): Path to the PDF file.
    
    Returns:
    list: List of transaction dictionaries.
    """
    with open(pdf_path, 'rb') as file:
        response = textract.analyze_document(
            Document={'Bytes': file.read()},
            FeatureTypes=['TABLES']
        )
    tables = get_tables_from_textract(response)
    transactions = []
    for table in tables:
        # Skip header row (assuming first row is header)
        for row in table[1:]:
            transaction = parse_transaction(row)
            if transaction:
                transactions.append(transaction)
    return transactions

def save_to_json(transactions, output_json_path):
    """
    Saves transactions to JSON file.
    """
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(transactions, json_file, indent=4, ensure_ascii=False)

# Usage example
if __name__ == "__main__":
    pdf_path = "data/August.pdf"  # Replace with your PDF path
    output_json_path = "data/aug.json"
    try:
        extracted_transactions = extract_transactions(pdf_path)
        save_to_json(extracted_transactions, output_json_path)
        print(f"Successfully extracted {len(extracted_transactions)} transactions and saved to {output_json_path}.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")