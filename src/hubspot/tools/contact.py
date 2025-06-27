import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from ..connection import get_access_token


class HubSpotListManager:
    """Handles HubSpot list operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def add_contact_to_list(self, list_id: str, contact_id: str) -> Dict[str, Any]:
        """
        Add a contact to a HubSpot static list.

        Args:
            list_id (str): The ID of the HubSpot list.
            contact_id (str): The ID of the contact to be added.

        Returns:
            dict: API response containing success or failure details.
        """
        payload = {"vids": [contact_id]}
        access_token = get_access_token()

        try:
            response = requests.post(
                f"{self.base_url}/contacts/v1/lists/{list_id}/add",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "response": data}
        except requests.exceptions.RequestException as e:
            error_message = (
                f"Error adding contact {contact_id} to list {list_id}: {str(e)}"
            )
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}

    def remove_contact_from_list(self, list_id: str, contact_id: str) -> Dict[str, Any]:
        """
        Remove a contact from a HubSpot static list.

        Args:
            list_id (str): The ID of the HubSpot list.
            contact_id (str): The ID of the contact to be removed.

        Returns:
            dict: API response containing success or failure details.
        """
        payload = {"vids": [contact_id]}
        access_token = get_access_token()
        
        try:
            response = requests.post(
                f"{self.base_url}/contacts/v1/lists/{list_id}/remove",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "response": data}
        except requests.exceptions.RequestException as e:
            error_message = f"Error removing contact {contact_id} from list {list_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactDeleter:
    """Handles HubSpot contact deletion operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def delete_contact_by_id(self, contact_id: str) -> Dict[str, Any]:
        """
        Delete a contact from HubSpot using their contact ID.

        Args:
            contact_id: HubSpot contact ID to delete.

        Returns:
            dict: Deletion status or error message.
        """
        try:
            # Build the delete endpoint URL
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            access_token = get_access_token()
            
            # Make DELETE request to HubSpot API
            response = requests.delete(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
            )

            # Raise exception for error status codes
            response.raise_for_status()
            
            # Return success response
            return {
                "status": "success",
                "message": f"Contact {contact_id} successfully deleted"
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error deleting HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}

    def delete_contact_by_email(self, email: str) -> Dict[str, Any]:
        """
        Delete a contact from HubSpot using their email address.
        First searches for the contact by email, then deletes if found.

        Args:
            email: Contact's email address to delete.

        Returns:
            dict: Deletion status or error message.
        """
        try:
            # First, search for the contact by email
            search_endpoint = f"{self.base_url}/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }]
                }]
            }
            access_token = get_access_token()

            search_response = requests.post(
                search_endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=search_payload
            )
            search_response.raise_for_status()
            
            result = search_response.json()
            
            if not result.get("total", 0):
                return {
                    "status": "failed",
                    "error": f"No contact found with email: {email}"
                }

            # Get the contact ID and delete the contact
            contact_id = result["results"][0]["id"]
            return self.delete_contact_by_id(contact_id)

        except requests.exceptions.RequestException as e:
            error_message = f"Error in contact deletion process: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactUpdater:
    """Handles HubSpot contact update operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def update_contact_by_email(self, email: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a contact in HubSpot using their email address as identifier.

        Args:
            email: Contact's email address to update.
            properties: Dictionary of properties to update.

        Returns:
            dict: Updated contact information or error message.
        """
        try:
            # Build the update endpoint URL using email as identifier
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/{email}?idProperty=email"
            
            # Prepare the update payload
            payload = {
                "properties": properties
            }
            access_token = get_access_token()

            # Make PATCH request to HubSpot API
            response = requests.patch(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload
            )

            # Raise exception for error status codes
            response.raise_for_status()
            
            return {
                "status": "success",
                "contact": response.json()
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error updating HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactSearcher:
    """Handles HubSpot contact search operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def search_contacts(self, email: str = "", firstname: str = "", phone: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Search for contacts in HubSpot using provided filters.

        Args:
            email: Email to search for (optional).
            firstname: First name to search for (optional).
            phone: Phone number to search for (optional).
            limit: Maximum number of contacts to return (default: 100).

        Returns:
            dict: Search results or error message.
        """
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/search"
            
            filters = []
            if email:
                filters.append({"propertyName": "email", "operator": "EQ", "value": email})
            if firstname:
                filters.append({"propertyName": "firstname", "operator": "EQ", "value": firstname})
            if phone:
                filters.append({"propertyName": "phone", "operator": "EQ", "value": phone})

            payload = {
                "filterGroups": [{"filters": filters}],
                "properties": ["email", "firstname", "phone"],
                "limit": limit
            }
            access_token = get_access_token()

            response = requests.post(
                endpoint, 
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }, 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "total": result.get("total", 0),
                "contacts": result.get("results", []),
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error searching contacts: {str(e)}"
            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactGetter:
    """Handles HubSpot contact retrieval operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def get_contact_by_email(self, email: str) -> Dict[str, Any]:
        """
        Retrieve a contact from HubSpot using their email address.

        Args:
            email: Contact's email address to search for.

        Returns:
            dict: Contact information or error message.
        """
        try:
            # Build the search endpoint URL with email filter
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/search"
            
            # Prepare the search criteria
            payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }]
                }]
            }
            access_token = get_access_token()
            
            # Make POST request to HubSpot Search API
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload
            )

            # Raise exception for error status codes
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            
            if not result.get("total", 0):
                return {
                    "status": "failed",
                    "error": f"No contact found with email: {email}"
                }

            # Return the first matching contact
            return {
                "status": "success",
                "contact": result["results"][0]
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotRecentContactsGetter:
    """Handles HubSpot recent contacts retrieval operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def get_recent_contacts(
        self,
        since: Optional[datetime] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Retrieve recently created or updated contacts from HubSpot.

        Args:
            since: DateTime object for filtering contacts modified after this time.
            limit: Maximum number of contacts to return (default: 10).

        Returns:
            dict: List of recent contacts or error message.
        """
        try:
            # Build the search endpoint URL
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/search"

            # Convert datetime to timestamp if provided
            timestamp = None
            if since:
                timestamp = int(since.timestamp() * 1000)  # Convert to milliseconds

            # Prepare the search criteria
            payload = {
                "filterGroups": [],
                "sorts": [
                    {"propertyName": "lastmodifieddate", "direction": "DESCENDING"}
                ],
                "limit": limit,
            }
            access_token = get_access_token()

            # Add time filter if specified
            if timestamp:
                payload["filterGroups"].append(
                    {
                        "filters": [
                            {
                                "propertyName": "lastmodifieddate",
                                "operator": "GTE",
                                "value": str(timestamp),
                            }
                        ]
                    }
                )

            # Make POST request to HubSpot Search API
            response = requests.post(
                endpoint, 
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }, 
                json=payload
            )

            # Raise exception for error status codes
            response.raise_for_status()

            result = response.json()

            return {
                "status": "success",
                "total": result.get("total", 0),
                "contacts": result.get("results", []),
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving recent contacts: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactCreator:
    """Handles HubSpot contact creation operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def create_contact(self, email: str, first_name: str, last_name: str, phone: str = None) -> Dict[str, Any]:
        """
        Create a contact in HubSpot using the direct API endpoint.

        Args:
            email: Contact's email address (required).
            first_name: Contact's first name.
            last_name: Contact's last name.
            phone: Contact's phone number (optional).

        Returns:
            dict: Response from HubSpot API.
        """
        try:
            # Prepare contact properties
            contact_properties = {
                "email": email,
                "firstname": first_name,
                "lastname": last_name,
            }
            
            if phone:
                contact_properties["phone"] = phone

            # Prepare request payload
            payload = {"properties": contact_properties}
            access_token = get_access_token()
            
            # Make POST request to HubSpot API
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # Raise exception for error status codes
            response.raise_for_status()

            return {
                "status": "success",
                "contact": response.json()
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error creating HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            print(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotClient:
    """Main HubSpot client that handles all company operations."""
    
    def __init__(self):
        self.base_url = "https://api.hubapi.com"

    def get_all_contacts(self) -> Dict[str, Any]:
        """Get all contacts from HubSpot."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/contacts"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            params = {
                "properties": "firstname,lastname,email,phone,company",
            }

            response = requests.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                error_message = (
                    f"API request failed: {response.status_code} {response.text}"
                )
                print(error_message)
                return {"result": None, "error": error_message}

            data = response.json()
            return {"result": data.get("results", []), "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message)
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message)
            return {"result": None, "error": error_message}
