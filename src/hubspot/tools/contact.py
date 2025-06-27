import os
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from ..connection import get_access_token

# Set up logging
logger = logging.getLogger(__name__)


class HubSpotListManager:
    """Handles HubSpot list operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
        headers = self._get_headers()

        try:
            logger.info(f"Adding contact {contact_id} to list {list_id}")
            response = requests.post(
                f"{self.base_url}/contacts/v1/lists/{list_id}/add",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully added contact {contact_id} to list {list_id}")
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

            logger.error(error_message)
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
        headers = self._get_headers()
        
        try:
            logger.info(f"Removing contact {contact_id} from list {list_id}")
            response = requests.post(
                f"{self.base_url}/contacts/v1/lists/{list_id}/remove",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully removed contact {contact_id} from list {list_id}")
            return {"status": "success", "response": data}
        except requests.exceptions.RequestException as e:
            error_message = f"Error removing contact {contact_id} from list {list_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(error_message)
            return {"status": "failed", "error": error_message}


class HubSpotContactDeleter:
    """Handles HubSpot contact deletion operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            headers = self._get_headers()
            
            logger.info(f"Deleting contact with ID: {contact_id}")
            # Make DELETE request to HubSpot API
            response = requests.delete(endpoint, headers=headers, timeout=30)

            # Raise exception for error status codes
            response.raise_for_status()
            
            # Return success response
            logger.info(f"Successfully deleted contact {contact_id}")
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

            logger.error(f"Failed to delete contact {contact_id}: {error_message}")
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
            headers = self._get_headers()

            logger.info(f"Searching for contact with email: {email}")
            search_response = requests.post(
                search_endpoint,
                headers=headers,
                json=search_payload,
                timeout=30
            )
            search_response.raise_for_status()
            
            result = search_response.json()
            
            if not result.get("total", 0):
                logger.warning(f"No contact found with email: {email}")
                return {
                    "status": "failed",
                    "error": f"No contact found with email: {email}"
                }

            # Get the contact ID and delete the contact
            contact_id = result["results"][0]["id"]
            logger.info(f"Found contact {contact_id} for email {email}, proceeding with deletion")
            return self.delete_contact_by_id(contact_id)

        except requests.exceptions.RequestException as e:
            error_message = f"Error in contact deletion process: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(f"Failed to delete contact by email {email}: {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotContactUpdater:
    """Handles HubSpot contact update operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            headers = self._get_headers()

            logger.info(f"Updating contact with email: {email}, properties: {list(properties.keys())}")
            # Make PATCH request to HubSpot API
            response = requests.patch(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )

            # Raise exception for error status codes
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully updated contact {email}")
            return {
                "status": "success",
                "contact": result
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error updating HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(f"Failed to update contact {email}: {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotContactSearcher:
    """Handles HubSpot contact search operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            search_criteria = []
            if email:
                filters.append({"propertyName": "email", "operator": "EQ", "value": email})
                search_criteria.append(f"email:{email}")
            if firstname:
                filters.append({"propertyName": "firstname", "operator": "EQ", "value": firstname})
                search_criteria.append(f"firstname:{firstname}")
            if phone:
                filters.append({"propertyName": "phone", "operator": "EQ", "value": phone})
                search_criteria.append(f"phone:{phone}")

            payload = {
                "filterGroups": [{"filters": filters}],
                "properties": ["email", "firstname", "phone"],
                "limit": limit
            }
            headers = self._get_headers()

            logger.info(f"Searching contacts with criteria: {', '.join(search_criteria)}, limit: {limit}")
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            total_found = result.get("total", 0)
            logger.info(f"Found {total_found} contacts matching search criteria")
            return {
                "status": "success",
                "total": total_found,
                "contacts": result.get("results", []),
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error searching contacts: {str(e)}"
            logger.error(f"Contact search failed: {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotContactGetter:
    """Handles HubSpot contact retrieval operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            headers = self._get_headers()
            
            logger.info(f"Fetching contact with email: {email}")
            # Make POST request to HubSpot Search API
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )

            # Raise exception for error status codes
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            
            if not result.get("total", 0):
                logger.warning(f"No contact found with email: {email}")
                return {
                    "status": "failed",
                    "error": f"No contact found with email: {email}"
                }

            # Return the first matching contact
            contact = result["results"][0]
            logger.info(f"Successfully found contact {contact.get('id')} with email: {email}")
            return {
                "status": "success",
                "contact": contact
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(f"Failed to get contact {email}: {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotRecentContactsGetter:
    """Handles HubSpot recent contacts retrieval operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            headers = self._get_headers()

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
                logger.info(f"Fetching recent contacts since {since}, limit: {limit}")
            else:
                logger.info(f"Fetching recent contacts, limit: {limit}")

            # Make POST request to HubSpot Search API
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=payload,
                timeout=30
            )

            # Raise exception for error status codes
            response.raise_for_status()

            result = response.json()
            total_found = result.get("total", 0)
            contacts = result.get("results", [])
            
            logger.info(f"Successfully retrieved {len(contacts)} recent contacts (total: {total_found})")
            return {
                "status": "success",
                "total": total_found,
                "contacts": contacts,
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving recent contacts: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(f"Failed to get recent contacts: {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotContactCreator:
    """Handles HubSpot contact creation operations."""
    
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

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
            headers = self._get_headers()
            
            logger.info(f"Creating contact: {first_name} {last_name} ({email})")
            # Make POST request to HubSpot API
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                headers=headers,
                json=payload,
                timeout=30
            )

            # Raise exception for error status codes
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully created contact {result.get('id')}: {first_name} {last_name} ({email})")
            return {
                "status": "success",
                "contact": result
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error creating HubSpot contact: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details}"
                except:
                    pass

            logger.error(f"Failed to create contact {first_name} {last_name} ({email}): {error_message}")
            return {"status": "failed", "error": error_message}


class HubSpotClient:
    """Main HubSpot client that handles all company operations."""
    
    def __init__(self):
        self.base_url = "https://api.hubapi.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        access_token = get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get_all_contacts(self) -> Dict[str, Any]:
        """Get all contacts from HubSpot."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/contacts"
            headers = self._get_headers()

            params = {
                "properties": "firstname,lastname,email,phone,company",
            }

            logger.info("Fetching all contacts")
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            if response.status_code != 200:
                error_message = (
                    f"API request failed: {response.status_code} {response.text}"
                )
                logger.error(f"Get all contacts failed: {error_message}")
                return {"result": None, "error": error_message}

            data = response.json()
            results = data.get("results", [])
            logger.info(f"Successfully retrieved {len(results)} contacts")
            return {"result": results, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while fetching all contacts: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error while fetching all contacts: {error_message}")
            return {"result": None, "error": error_message}
