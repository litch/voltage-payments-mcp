import os
import requests
from typing import Dict, Any, Optional

class VoltageAPIClient:
    """Client for making requests to the Voltage API."""
    
    def __init__(self):
        """Initialize the client with environment variables."""
        self.base_url = os.environ.get("BASE_URL")
        self.api_key = os.environ.get("API_KEY")
        self.organization_id = os.environ.get("ORGANIZATION_ID")
        self.environment_id = os.environ.get("ENVIRONMENT_ID")
        
        if not all([self.base_url, self.api_key, self.organization_id, self.environment_id]):
            raise ValueError("Missing required environment variables: BASE_URL, API_KEY, ORGANIZATION_ID, ENVIRONMENT_ID")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_all_wallets(self) -> Dict[str, Any]:
        """
        Get all wallets for the organization.
        
        Returns:
            Dict[str, Any]: The API response containing the wallets.
        """
        url = f"{self.base_url}/api/v1/organizations/{self.organization_id}/wallets"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
