import os
import requests
from typing import Dict, Any, List
import uuid
import json
import sys
import time

class VoltagePaymentsAPI:
    """
    A class to interact with the Voltage Payments API.
    Implements specific API endpoints as methods.
    """

    def __init__(self):
        """Initialize the API client with environment variables."""
        self.base_url = os.environ.get("BASE_URL") + "/api/v1"
        self.api_key = os.environ.get("API_KEY")
        self.organization_id = os.environ.get("ORGANIZATION_ID")
        self.environment_id = os.environ.get("ENVIRONMENT_ID")

        if not all([self.base_url, self.api_key, self.organization_id, self.environment_id]):
            raise ValueError("Missing required environment variables: BASE_URL, API_KEY, ORGANIZATION_ID, ENVIRONMENT_ID")

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        return {
            "Content-Type": "application/json",
            "X-API-Key": f"{self.api_key}"
        }

    def get_all_wallets(self) -> List[Dict[str, Any]]:
        """
        Get all wallets for the organization.

        This method calls the 'get_all_organizations_wallets_as_user' endpoint from the API.

        Returns:
            List[Dict[str, Any]]: A list of wallet objects.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/organizations/{self.organization_id}/wallets"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def generate_bolt11_invoice(self, wallet_id: str, amount_sats: int, memo: str = None) -> Dict[str, Any]:
        """
        Generate a BOLT11 invoice for receiving a payment.
        
        Args:
            wallet_id: The ID of the wallet to generate the invoice for.
            amount_sats: The amount in satoshis to request.
            memo: Optional description/memo for the invoice.
            
        Returns:
            Dict[str, Any]: The generated invoice data including the payment request string.
            
        Raises:
            requests.HTTPError: If the API request fails.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/environments/{self.environment_id}/payments"
            print(f"Request URL: {url}", file=sys.stderr)
            
            # Convert satoshis to millisatoshis
            amount_msats = amount_sats * 1000
            
            # Create a payment ID that we'll use for both creating and retrieving the payment
            payment_id = str(uuid.uuid4())
            
            # Create payload according to the receive_payment_bolt11 example in the API spec
            payload = {
                "id": payment_id,
                "wallet_id": wallet_id,
                "currency": "btc",
                "payment_kind": "bolt11",
                "amount_msats": amount_msats
            }
            
            if memo:
                payload["description"] = memo
            
            print(f"Request payload: {json.dumps(payload)}", file=sys.stderr)
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            # For 202 responses, the request was accepted but we need to poll for the result
            if response.status_code == 202:
                print(f"Payment request accepted, polling for payment details...", file=sys.stderr)
                return self._poll_payment_status(payment_id)
            
            # For other successful responses, parse the JSON
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise
    
    def _poll_payment_status(self, payment_id: str, max_attempts: int = 5, delay_seconds: int = 2) -> Dict[str, Any]:
        """
        Poll the payment status endpoint until the payment is ready or max attempts are reached.
        
        Args:
            payment_id: The ID of the payment to poll for.
            max_attempts: Maximum number of polling attempts.
            delay_seconds: Delay between polling attempts in seconds.
            
        Returns:
            Dict[str, Any]: The payment details.
            
        Raises:
            ValueError: If polling times out or the payment cannot be found.
        """
        url = f"{self.base_url}/organizations/{self.organization_id}/environments/{self.environment_id}/payments/{payment_id}"
        print(f"Polling URL: {url}", file=sys.stderr)
        
        for attempt in range(max_attempts):
            try:
                print(f"Polling attempt {attempt + 1}/{max_attempts}...", file=sys.stderr)
                response = requests.get(url, headers=self._get_headers())
                print(f"Poll response status: {response.status_code}", file=sys.stderr)
                
                if response.status_code == 200:
                    try:
                        payment_data = response.json()
                        print(f"Payment data: {json.dumps(payment_data)}", file=sys.stderr)
                        return payment_data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error during polling: {e}", file=sys.stderr)
                        print(f"Response content: {response.text}", file=sys.stderr)
                
                # If we get a 404, the payment might not be ready yet
                if response.status_code == 404:
                    print("Payment not found yet, waiting...", file=sys.stderr)
                
                # Wait before trying again
                time.sleep(delay_seconds)
                
            except requests.RequestException as e:
                print(f"Error during polling: {e}", file=sys.stderr)
                # Continue polling despite errors
        
        raise ValueError(f"Failed to retrieve payment details after {max_attempts} attempts")
    
    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check the status of a payment by its ID.
        
        Args:
            payment_id: The ID of the payment to check.
            
        Returns:
            Dict[str, Any]: The payment details including its current status.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the payment cannot be found or the response is invalid.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/environments/{self.environment_id}/payments/{payment_id}"
            print(f"Checking payment status URL: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=self._get_headers())
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            response.raise_for_status()
            
            try:
                payment_data = response.json()
                return payment_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def pay_bolt11_invoice(self, wallet_id: str, payment_request: str, amount_sats: int = None, fee_limit_sats: int = None) -> Dict[str, Any]:
        """
        Pay a BOLT11 invoice.
        
        Args:
            wallet_id: The ID of the wallet to pay from.
            payment_request: The BOLT11 payment request string to pay.
            amount_sats: Optional amount in satoshis to pay (for zero-amount invoices).
            fee_limit_sats: Optional maximum fee in satoshis to pay for the payment.
            
        Returns:
            Dict[str, Any]: The payment result data.
            
        Raises:
            requests.HTTPError: If the API request fails.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/environments/{self.environment_id}/payments"
            print(f"Request URL: {url}", file=sys.stderr)
            
            # Create a payment ID that we'll use for both creating and retrieving the payment
            payment_id = str(uuid.uuid4())
            
            # Create the data object for the payment according to send_payment_bolt11 example
            data = {
                "payment_request": payment_request
            }
            
            # Convert satoshis to millisatoshis if provided
            if amount_sats is not None:
                data["amount_msats"] = amount_sats * 1000
                
            if fee_limit_sats is not None:
                data["max_fee_msats"] = fee_limit_sats * 1000
                
            payload = {
                "id": payment_id,
                "wallet_id": wallet_id,
                "currency": "btc",
                "type": "bolt11",
                "data": data
            }
            
            print(f"Request payload: {json.dumps(payload)}", file=sys.stderr)
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            # For 202 responses, the request was accepted but we need to poll for the result
            if response.status_code == 202:
                print(f"Payment request accepted, polling for payment details...", file=sys.stderr)
                return self._poll_payment_status(payment_id)
            
            # For other successful responses, parse the JSON
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def create_wallet(self, wallet_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new wallet in the organization.
        
        Args:
            wallet_request: A dictionary containing the wallet creation parameters.
                Must include: id, environment_id, line_of_credit_id, name, network, limit
                
        Returns:
            Dict[str, Any]: The created wallet object.
            
        Raises:
            requests.HTTPError: If the API request fails.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/wallets"
            print(f"Request URL: {url}", file=sys.stderr)
            
            print(f"Request payload: {json.dumps(wallet_request)}", file=sys.stderr)
            
            response = requests.post(url, headers=self._get_headers(), json=wallet_request)
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            # For 202 responses, the request was accepted
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def get_wallet(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get a specific wallet by its ID.
        
        Args:
            wallet_id: The ID of the wallet to retrieve.
            
        Returns:
            Dict[str, Any]: The wallet object.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the wallet cannot be found or the response is invalid.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/wallets/{wallet_id}"
            print(f"Request URL: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=self._get_headers())
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            response.raise_for_status()
            
            try:
                wallet_data = response.json()
                return wallet_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def delete_wallet(self, wallet_id: str) -> Dict[str, Any]:
        """
        Delete a specific wallet by its ID.
        
        Args:
            wallet_id: The ID of the wallet to delete.
            
        Returns:
            Dict[str, Any]: The response data, typically a success message or empty.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the wallet cannot be found or the response is invalid.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/wallets/{wallet_id}"
            print(f"Request URL: {url}", file=sys.stderr)
            
            response = requests.delete(url, headers=self._get_headers())
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            response.raise_for_status()
            
            # If the response is empty (common for DELETE operations), return a success message
            if not response.text.strip():
                return {"success": True, "message": f"Wallet {wallet_id} deleted successfully"}
            
            # Otherwise try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def get_wallet_ledger_as_user(self, wallet_id: str, offset: int = None, limit: int = None, 
                                 payment_id: str = None, start_date: str = None, end_date: str = None,
                                 sort_key: str = None, sort_order: str = None) -> Dict[str, Any]:
        """
        Get the ledger for a specific wallet by its ID.
        
        Args:
            wallet_id: The ID of the wallet to retrieve the ledger for.
            offset: Optional, pagination offset for ledger items.
            limit: Optional, maximum number of ledger items to return.
            payment_id: Optional, filter ledger items by payment ID.
            start_date: Optional, filter ledger items by start date (ISO 8601 format).
            end_date: Optional, filter ledger items by end date (ISO 8601 format).
            sort_key: Optional, key to sort the ledger items by (effective_time, message_time, or time_and_effective_time).
            sort_order: Optional, order to sort the ledger items (asc or desc).
            
        Returns:
            Dict[str, Any]: The wallet ledger object containing items, offset, limit, and total.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the wallet cannot be found or the response is invalid.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/wallets/{wallet_id}/ledger"
            print(f"Request URL: {url}", file=sys.stderr)
            
            # Build query parameters
            params = {}
            if offset is not None:
                params['offset'] = offset
            if limit is not None:
                params['limit'] = limit
            if payment_id is not None:
                params['payment_id'] = payment_id
            if start_date is not None:
                params['start_date'] = start_date
            if end_date is not None:
                params['end_date'] = end_date
            if sort_key is not None:
                params['sort_key'] = sort_key
            if sort_order is not None:
                params['sort_order'] = sort_order
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            response.raise_for_status()
            
            try:
                ledger_data = response.json()
                return ledger_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise

    def get_payments(self, offset: int = None, limit: int = None, wallet_id: str = None,
                    statuses: List[str] = None, sort_key: str = None, sort_order: str = None,
                    kind: str = None, direction: str = None, start_date: str = None, 
                    end_date: str = None) -> Dict[str, Any]:
        """
        Get a list of payments with optional filtering parameters.
        
        Args:
            offset: Optional, pagination offset for payment items.
            limit: Optional, maximum number of payment items to return.
            wallet_id: Optional, filter payments by wallet ID.
            statuses: Optional, filter payments by status (list of status strings).
            sort_key: Optional, key to sort the payments by (created_at or updated_at).
            sort_order: Optional, order to sort the payments (ASC or DESC).
            kind: Optional, filter payments by kind (bolt11, onchain, or bip21).
            direction: Optional, filter payments by direction (send or receive).
            start_date: Optional, filter payments by start date (ISO 8601 format).
            end_date: Optional, filter payments by end date (ISO 8601 format).
            
        Returns:
            Dict[str, Any]: The payments object containing items, offset, limit, and total.
            
        Raises:
            requests.HTTPError: If the API request fails.
            ValueError: If the response is invalid.
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization_id}/environments/{self.environment_id}/payments"
            print(f"Request URL: {url}", file=sys.stderr)
            
            # Build query parameters
            params = {}
            if offset is not None:
                params['offset'] = offset
            if limit is not None:
                params['limit'] = limit
            if wallet_id is not None:
                params['wallet_id'] = wallet_id
            if statuses is not None:
                params['statuses'] = statuses
            if sort_key is not None:
                params['sort_key'] = sort_key
            if sort_order is not None:
                params['sort_order'] = sort_order
            if kind is not None:
                params['kind'] = kind
            if direction is not None:
                params['direction'] = direction
            if start_date is not None:
                params['start_date'] = start_date
            if end_date is not None:
                params['end_date'] = end_date
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            print(f"Response status code: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            print(f"Response content: {response.text}", file=sys.stderr)
            
            response.raise_for_status()
            
            try:
                payments_data = response.json()
                return payments_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                print(f"Response content: {response.text}", file=sys.stderr)
                raise ValueError(f"Invalid JSON response from API: {e}")
                
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Error response content: {e.response.text}", file=sys.stderr)
            raise
