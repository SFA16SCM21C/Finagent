import os
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from dotenv import load_dotenv

def initialize_plaid_client():
    """Initialize and return a Plaid API client for the sandbox environment."""
    load_dotenv()
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    env = os.getenv("PLAID_ENV")

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
    return plaid_api.PlaidApi(api_client)

def create_public_token(client):
    """Create a public token for ins_109508."""
    try:
        pt_request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",
            initial_products=[Products('transactions')]
        )
        pt_response = client.sandbox_public_token_create(pt_request)
        return pt_response.public_token
    except Exception as e:
        raise Exception(f"Error creating public token: {e}")

def exchange_public_token(client, public_token):
    """Exchange a public token for an access token."""
    try:
        at_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        at_response = client.item_public_token_exchange(at_request)
        return at_response.access_token
    except Exception as e:
        raise Exception(f"Error exchanging public token: {e}")

def sync_transactions(client, access_token):
    """Fetch the first batch of transactions using the sync endpoint."""
    try:
        request = TransactionsSyncRequest(
            access_token=access_token
        )
        response = client.transactions_sync(request)
        return response['added']
    except Exception as e:
        raise Exception(f"Error syncing transactions: {e}")