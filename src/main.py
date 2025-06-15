from src.transactions import fetch_and_save_transactions

def main():
    """Main function to run the FinAgent transaction pipeline."""
    print("Starting FinAgent transaction pipeline...")
    transactions = fetch_and_save_transactions()
    print("Pipeline completed.")

if __name__ == "__main__":
    main()