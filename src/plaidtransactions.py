import os
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
client_id = os.getenv("PLAID_CLIENT_ID")
secret = os.getenv("PLAID_SECRET")
env = os.getenv("PLAID_ENV")

# Validate environment variables
if not all([client_id, secret, env]):
    raise ValueError("Missing required environment variables in .env file")

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
        'plaidVersion': '2020-09-14'
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

try:
    # Step 1: Create a public token in sandbox
    print("Env loaded with details")
    
    pt_request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products('transactions')]
    )
    pt_response = client.sandbox_public_token_create(pt_request)
    public_token = pt_response.public_token
    
    print("Public token generated")
    
    # Step 2: Exchange public token for access token
    at_request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    at_response = client.item_public_token_exchange(at_request)
    #access_token = at_response.access_token
    access_token = 'access-sandbox-9edbddce-23cc-4f2e-8614-2cfea6713146'
    
    print("Access token generated")
    
    # Step 3: Fetch transactions for the last 30 days
    request = TransactionsSyncRequest(
        access_token=access_token,
    )
    response = client.transactions_sync(request)
    transactions = response['added']
    
    print("Transactions found")
    while (response['has_more']):
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response['next_cursor']
        )
        response = client.transactions_sync(request)
        transactions += response['added']
        
    
    for transaction in transactions:
        name = transaction.name
        date = transaction.date
        amount = transaction.amount
        print(f"Transaction on {date} at {date}: ${amount:.2f}")

except Exception as e:
    print(f"Error: {e}")