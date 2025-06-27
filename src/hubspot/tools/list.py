import os
import requests
from typing import Dict, Literal
from ..connection import  get_access_token

class HubSpotListCreator:
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.access_token = get_access_token()
        self.base_url = "https://api.hubapi.com"

    def _get_object_type_id(self, list_type: Literal["CONTACTS", "COMPANIES"]) -> str:
        """Convert list_type to HubSpot's objectTypeId format."""
        type_mapping = {
            "CONTACTS": "0-1",  # HubSpot's ID for contacts
            "COMPANIES": "0-2",  # HubSpot's ID for companies
        }
        return type_mapping[list_type]

    def create_static_list(
        self,
        name: str,
        list_type: Literal["CONTACTS", "COMPANIES"] = "CONTACTS",
        
    ) -> Dict:
        """
        Create a static list in HubSpot.

        Args:
            name: Name of the list
            list_type: Type of list (CONTACTS or COMPANIES)
            folder_id: ID of the folder to place the list in (optional)

        Returns:
            dict: Response from HubSpot API
        """
        try:
            payload = {
                "name": name,
                "objectTypeId": self._get_object_type_id(list_type),
                "processingType": "MANUAL",
            }
            access_token = get_access_token()   

            response = requests.post(
                f"{self.base_url}/crm/v3/lists", headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }, json=payload
            )

            response.raise_for_status()
            return {"status": "success", "list": response.json()}

        except requests.exceptions.RequestException as e:
            error_message = f"Error creating HubSpot list: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}
    def delete_list(self, list_id: str) -> Dict:
        """
        Delete a list from HubSpot.

        Args:
            list_id (str): The ID of the HubSpot list to delete.

        Returns:
            dict: API response containing success or failure details.
        """
        try:
            access_token = get_access_token()   
            response = requests.delete(
                f"{self.base_url}/crm/v3/lists/{list_id}",
                headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
            )
            response.raise_for_status()
            return {
                "status": "success",
                "message": f"List {list_id} deleted successfully",
            }
        except requests.exceptions.RequestException as e:
            error_message = f"Error deleting HubSpot list {list_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}