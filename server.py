# server.py
import sys
from mcp.server.fastmcp import FastMCP
from voltage_payments_api import VoltagePaymentsAPI

try:
    # Create an MCP server
    print("Creating MCP server...", file=sys.stderr)
    mcp = FastMCP("Voltage Payments API")

    # Initialize the Voltage Payments API client
    voltage_api = VoltagePaymentsAPI()

    # Add a tool to get all wallets
    @mcp.tool()
    def get_all_wallets() -> list:
        """Get all wallets for the organization"""
        print("Getting all wallets...", file=sys.stderr)
        return voltage_api.get_all_wallets()

    # Add a tool to generate a BOLT11 invoice
    @mcp.tool()
    def generate_bolt11_invoice(wallet_id: str, amount_sats: int, memo: str = None) -> dict:
        """
        Generate a BOLT11 invoice for receiving a payment

        Args:
            wallet_id: The ID of the wallet to generate the invoice for
            amount_sats: The amount in satoshis to request
            memo: Optional description/memo for the invoice
        """
        print(f"Generating BOLT11 invoice for wallet {wallet_id}...", file=sys.stderr)
        return voltage_api.generate_bolt11_invoice(wallet_id, amount_sats, memo)

    # Add a tool to pay a BOLT11 invoice
    @mcp.tool()
    def pay_bolt11_invoice(wallet_id: str, payment_request: str, amount_sats: int = None, fee_limit_sats: int = None) -> dict:
        """
        Pay a BOLT11 invoice

        Args:
            wallet_id: The ID of the wallet to pay from
            payment_request: The BOLT11 payment request string to pay
            amount_sats: Optional amount in satoshis to pay (for zero-amount invoices)
            fee_limit_sats: Optional maximum fee in satoshis to pay for the payment
        """
        print(f"Paying BOLT11 invoice from wallet {wallet_id}...", file=sys.stderr)
        return voltage_api.pay_bolt11_invoice(wallet_id, payment_request, amount_sats, fee_limit_sats)

    # Add a tool to check payment status
    @mcp.tool()
    def check_payment_status(payment_id: str) -> dict:
        """
        Check the status of a payment by its ID

        Args:
            payment_id: The ID of the payment to check
        """
        print(f"Checking payment status for payment {payment_id}...", file=sys.stderr)
        return voltage_api.check_payment_status(payment_id)

    # Add a tool to create a wallet
    @mcp.tool()
    def create_wallet(wallet_request: dict) -> dict:
        """
        Create a new wallet in the organization

        Args:
            wallet_request: A dictionary containing the wallet creation parameters.
                Must include: id, environment_id, line_of_credit_id, name, network, limit
        """
        print(f"Creating wallet with request: {wallet_request}...", file=sys.stderr)
        return voltage_api.create_wallet(wallet_request)

    # Add a tool to get a wallet
    @mcp.tool()
    def get_wallet(wallet_id: str) -> dict:
        """
        Get a specific wallet by its ID

        Args:
            wallet_id: The ID of the wallet to retrieve
        """
        print(f"Getting wallet with ID: {wallet_id}...", file=sys.stderr)
        return voltage_api.get_wallet(wallet_id)

    # Add a tool to delete a wallet
    @mcp.tool()
    def delete_wallet(wallet_id: str) -> dict:
        """
        Delete a specific wallet by its ID

        Args:
            wallet_id: The ID of the wallet to delete
        """
        print(f"Deleting wallet with ID: {wallet_id}...", file=sys.stderr)
        return voltage_api.delete_wallet(wallet_id)

    # Add a tool to get a wallet's ledger
    @mcp.tool()
    def get_wallet_ledger_as_user(wallet_id: str, offset: int = None, limit: int = None, 
                                 payment_id: str = None, start_date: str = None, end_date: str = None,
                                 sort_key: str = None, sort_order: str = None) -> dict:
        """
        Get the ledger for a specific wallet by its ID

        Args:
            wallet_id: The ID of the wallet to retrieve the ledger for
            offset: Optional, pagination offset for ledger items
            limit: Optional, maximum number of ledger items to return
            payment_id: Optional, filter ledger items by payment ID
            start_date: Optional, filter ledger items by start date (ISO 8601 format)
            end_date: Optional, filter ledger items by end date (ISO 8601 format)
            sort_key: Optional, key to sort the ledger items by (effective_time, message_time, or time_and_effective_time)
            sort_order: Optional, order to sort the ledger items (ASC or DESC)
        """
        print(f"Getting ledger for wallet with ID: {wallet_id}...", file=sys.stderr)
        return voltage_api.get_wallet_ledger_as_user(wallet_id, offset, limit, payment_id, 
                                                   start_date, end_date, sort_key, sort_order)

    # Add a tool to get payments
    @mcp.tool()
    def get_payments(offset: int = None, limit: int = None, wallet_id: str = None,
                    statuses: list = None, sort_key: str = None, sort_order: str = None,
                    kind: str = None, direction: str = None, start_date: str = None, 
                    end_date: str = None) -> dict:
        """
        Get a list of payments with optional filtering parameters

        Args:
            offset: Optional, pagination offset for payment items
            limit: Optional, maximum number of payment items to return
            wallet_id: Optional, filter payments by wallet ID
            statuses: Optional, filter payments by status (list of status strings)
            sort_key: Optional, key to sort the payments by (created_at or updated_at)
            sort_order: Optional, order to sort the payments (ASC or DESC)
            kind: Optional, filter payments by kind (bolt11, onchain, or bip21)
            direction: Optional, filter payments by direction (send or receive)
            start_date: Optional, filter payments by start date (ISO 8601 format)
            end_date: Optional, filter payments by end date (ISO 8601 format)
        """
        print(f"Getting payments with filters...", file=sys.stderr)
        return voltage_api.get_payments(offset, limit, wallet_id, statuses, sort_key, 
                                      sort_order, kind, direction, start_date, end_date)

    print("Server setup complete, ready to run", file=sys.stderr)
except Exception as e:
    print(f"Error setting up server: {e}", file=sys.stderr)
    raise