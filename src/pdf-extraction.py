import pdfplumber
import re
import json
import os

def convert_date_format(date_str):
    """
    Converts date from DD.MM.YYYY to YYYY-MM-DD format.
    
    Parameters:
    date_str (str): Date in DD.MM.YYYY format.
    
    Returns:
    str: Date in YYYY-MM-DD format, or None if invalid.
    """
    try:
        day, month, year = date_str.split('.')
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except (ValueError, AttributeError):
        return None

def parse_description(description):
    """
    Parses the multi-line description string into merchant, category, additional details, and value date.
    
    Parameters:
    description (str): The raw description text from the table cell.
    
    Returns:
    dict: Parsed components including merchant, category, additional_details, and value_date.
    """
    value_date_pattern = re.compile(r'Fecha de valor (\d{2}\.\d{2}\.\d{4})')
    value_date = None
    parts = [line.strip() for line in description.split('\n') if line.strip()]
    
    if not parts:
        return {"merchant": "", "category": "", "additional_details": "", "value_date": None}
    
    merchant = parts[0]
    category = parts[1].replace(' • ', ' ') if len(parts) > 1 else ""
    additional_details = []
    
    for dl in parts[2:]:
        match = value_date_pattern.search(dl)
        if match:
            value_date = match.group(1)
        else:
            additional_details.append(dl.replace(' • ', ' '))  # Clean dot markers in additional details as well
    
    # If value date is embedded in earlier lines, extract it
    for i, part in enumerate(parts):
        match = value_date_pattern.search(part)
        if match:
            value_date = match.group(1)
            parts[i] = part.replace(f'Fecha de valor {value_date}', '').strip()
    
    return {
        "merchant": merchant,
        "category": category,
        "additional_details": ' '.join(additional_details),
        "value_date": value_date
    }

def extract_transactions(pdf_path):
    """
    Extracts transaction data from the PDF bank statement using table detection as primary method,
    with fallback to line-by-line parsing.
    
    Parameters:
    pdf_path (str): Path to the PDF file.
    
    Returns:
    list: List of dictionaries, each representing a transaction.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text or "Resumen" in text or "Nota" in text:
                continue  # Skip summary and notes pages
            
            # Primary: Extract tables
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    in_transaction = False
                    for row in table:
                        if not row or all(not cell for cell in row):
                            continue
                        
                        # Detect transaction table header (requires all three columns to distinguish from summary)
                        row_str = [str(cell) for cell in row]
                        if "Descripción" in row_str and "Fecha de reserva" in row_str and "Cantidad" in row_str:
                            in_transaction = True
                            continue
                        
                        if not in_transaction:
                            continue
                        
                        # Parse row: description (col 0), booking_date (col 1), amount (col 2)
                        description = str(row[0]) if len(row) > 0 else ""
                        booking_date = str(row[1]) if len(row) > 1 and re.match(r'^\d{2}\.\d{2}\.\d{4}$', str(row[1]).strip()) else None
                        amount_str = str(row[2]) if len(row) > 2 and re.match(r'^[+-]?\d{1,3}(?:\.\d{3})*,\d{2}€$', str(row[2]).strip()) else ""
                        
                        if description and amount_str and booking_date:
                            # Parse amount
                            amount_clean = amount_str.replace('€', '').strip().replace('.', '').replace(',', '.')
                            amount = float(amount_clean)
                            
                            # Parse description
                            parsed_desc = parse_description(description)
                            value_date = parsed_desc["value_date"]
                            
                            # Only add if it's a valid transaction (e.g., has value_date)
                            if value_date:
                                transactions.append({
                                    "merchant_or_person": parsed_desc["merchant"],
                                    "category_or_type": parsed_desc["category"],
                                    "additional_details": parsed_desc["additional_details"],
                                    "value_date": convert_date_format(value_date),
                                    "booking_date": convert_date_format(booking_date),
                                    "amount": amount
                                })
            else:
                # Fallback: Line-by-line parsing for non-tabular pages
                lines = text.strip().split('\n')
                current_transaction = []
                in_transaction_section = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if "Descripción" in line and "Fecha de reserva" in line and "Cantidad" in line:
                        in_transaction_section = True
                        continue
                    
                    if 'Extracto bancario' in line or 'hasta' in line or 'Resumen' in line or 'Nota' in line:
                        in_transaction_section = False
                        continue
                    
                    if in_transaction_section:
                        current_transaction.append(line)
                        
                        if re.match(r'^[+-]?\d{1,3}(?:\.\d{3})*,\d{2}€$', line):
                            if current_transaction:
                                amount_str = current_transaction.pop().replace('€', '').replace('.', '').replace(',', '.')
                                amount = float(amount_str)
                                booking_date_str = current_transaction.pop() if current_transaction and re.match(r'^\d{2}\.\d{2}\.\d{4}$', current_transaction[-1]) else ""
                                description = '\n'.join(current_transaction)
                                
                                parsed_desc = parse_description(description)
                                value_date = parsed_desc["value_date"]
                                
                                if value_date and booking_date_str:
                                    transactions.append({
                                        "merchant_or_person": parsed_desc["merchant"],
                                        "category_or_type": parsed_desc["category"],
                                        "additional_details": parsed_desc["additional_details"],
                                        "value_date": convert_date_format(value_date),
                                        "booking_date": convert_date_format(booking_date_str),
                                        "amount": amount
                                    })
                            current_transaction = []
    
    return transactions

def save_to_json(transactions, output_path):
    """
    Saves the list of transactions to a JSON file.
    
    Parameters:
    transactions (list): List of transaction dictionaries.
    output_path (str): Path to the output JSON file.
    """
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(transactions, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    pdf_path = "data/August.pdf"  # Replace with the actual path to your PDF file
    output_json_path = "data/aug.json"  # Output file name
    
    try:
        extracted_transactions = extract_transactions(pdf_path)
        save_to_json(extracted_transactions, output_json_path)
        print(f"Successfully extracted {len(extracted_transactions)} transactions and saved to {output_json_path}.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")