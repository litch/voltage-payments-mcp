import os
import requests
from typing import Dict, Any, List

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
