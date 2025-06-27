import os
import requests
from datetime import datetime, timezone
from typing import Dict,Optional,Any
from dateutil import parser
from ..connection import get_access_token

class HubSpotTicketCreator:
    def __init__(self):
        """Initialize HubSpot API configuration using OAuth access token."""
        self.access_token = get_access_token()
        self.base_url = "https://api.hubapi.com"

    def create_ticket(
        self,
        subject: str,
        content: str,
        pipeline: str = "0",  # Default support pipeline
        pipeline_stage: str = "1",  # Default to first stage
        priority: str = "MEDIUM",
        category: str = "",
        contact_id: str = "",
        owner_id: str = "",
        source_type: str = "",
    ) -> Dict:
        """
        Create a ticket in HubSpot using the direct API endpoint.

        Args:
            subject: Ticket subject/title
            content: Ticket description/content
            pipeline: Pipeline ID (default: "0" for support pipeline)
            pipeline_stage: Stage ID within the pipeline (1 = New,2 = Waiting on contact,3 = Waiting on us,4 = closed)
            priority: Ticket priority (LOW, MEDIUM, HIGH)
            category: Ticket category (PRODUCT_ISSUE,BILLING_ISSUE,FEATURE_REQUEST,GENERAL_INQUIRY)(optional)
            contact_id: Associated contact ID (optional)
            owner_id: HubSpot owner ID (optional)
            source_type: Channel where ticket was submitted (CHAT, EMAIL, FORM, PHONE) (optional)

        Returns:
            dict: Response from HubSpot API
        """
        try:
            # Prepare ticket properties
            ticket_properties = {
                "subject": subject,
                "content": content,
                "hs_pipeline": pipeline,
                "hs_pipeline_stage": pipeline_stage,
                "hs_ticket_priority": priority,
            }

            # Add optional properties if provided
            if category:
                ticket_properties["hs_ticket_category"] = category
            if owner_id:
                ticket_properties["hubspot_owner_id"] = owner_id
            if source_type:
                ticket_properties["source_type"] = source_type

            # Prepare request payload
            payload = {
                "properties": ticket_properties,
            }
            access_token= get_access_token()

            # Prepare associations list
            associations = []

            # Add contact association if provided
            if contact_id:
                associations.append(
                    {
                        "to": {"id": contact_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 16,
                            }
                        ],
                    }
                )

            # Add associations to payload if any exist
            if associations:
                payload["associations"] = associations

            # Make POST request to HubSpot API
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/tickets",
                headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
                json=payload,
            )

            # Raise exception for error status codes
            response.raise_for_status()

            return {"status": "success", "ticket": response.json()}

        except requests.exceptions.RequestException as e:
            error_message = f"Error creating HubSpot ticket: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}
    
    def get_ticket_by_id(self, ticket_id: str) -> Dict:
        """
        Fetch a single ticket by ticket ID with all properties and associations.
        """
        params = {
            "properties": "*",  # Fetch all available properties
            "associations": "contacts,companies,deals",  # Include related entities
        }
        access_token = get_access_token()

        try:
            response = requests.get(
                f"{self.base_url}/crm/v3/objects/tickets/{ticket_id}",
                 headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "ticket": data}
        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching HubSpot ticket {ticket_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}
        
    def delete_ticket_by_id(self, ticket_id: str) -> Dict:
        """
        Delete a ticket by its ID.
        """
        try:
            access_token = get_access_token()
            response = requests.delete(
                f"{self.base_url}/crm/v3/objects/tickets/{ticket_id}",
                headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
            )
            response.raise_for_status()
            return {"status": "success", "message": f"Ticket {ticket_id} deleted successfully"}
        except requests.exceptions.RequestException as e:
            error_message = f"Error deleting HubSpot ticket {ticket_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}
        
    
    def update_ticket_by_id(
        self,
        ticket_id: str,
        subject: str = "",
        description: str = "",
        hs_pipeline: str = "",
        hs_pipeline_stage: str = "",
        priority: str = "",
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """
        Update a ticket with optional fields.

        Args:
            ticket_id (str): The ID of the HubSpot ticket to update.
            subject (str, optional): New ticket subject.
            description (str, optional): New ticket description.
            hs_pipeline (str, optional): New pipeline ID.
            hs_pipeline_stage (str, optional): New pipeline stage ID(1 = New,2 = Waiting on contact,3 = Waiting on us,4 = closed).
            priority (str, optional):new priority(LOW, MEDIUM, HIGH)
            properties (dict, optional): Additional properties to update.

        Returns:
            dict: API response containing success or failure details.
        """
        properties = properties or {}

        # Add non-empty values to properties dictionary
        if subject:
            properties["subject"] = subject
        if description:
            properties["content"] = description
        if hs_pipeline:
            properties["hs_pipeline"] = hs_pipeline
        if hs_pipeline_stage:
            properties["hs_pipeline_stage"] = hs_pipeline_stage
        if priority:
            properties["hs_ticket_priority"] = priority

        if not properties:
            return {"status": "failed", "error": "No valid properties to update."}

        payload = {"properties": properties}

        try:
            access_token = get_access_token()
            response = requests.patch(
                f"{self.base_url}/crm/v3/objects/tickets/{ticket_id}",
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "updated_ticket": data}
        except requests.exceptions.RequestException as e:
            error_message = f"Error updating HubSpot ticket {ticket_id}: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}
        
    def get_tickets(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> Dict:
        """
        Fetch tickets from HubSpot based on date range.

        Args:
            start_date: Start datetime
            end_date: End datetime
            limit: Maximum number of tickets to return (default: 100)
        Returns:
            dict: Response containing tickets and pagination info
        """
        try:
            # Convert datetime to UTC timestamps in milliseconds
            start_timestamp = int(
                start_date.astimezone(timezone.utc).timestamp() * 1000
            )
            end_timestamp = int(end_date.astimezone(timezone.utc).timestamp() * 1000)

            # Build filter for date range (fixing BETWEEN operator issue)
            filter_groups = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "createdate",
                                "operator": "BETWEEN",
                                "value": start_timestamp,
                                "highValue": end_timestamp,
                            }
                        ]
                    }
                ]
            }

            # Prepare query parameters
            params = {
                "limit": limit,
            }

            # Make POST request to HubSpot Search API
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/tickets/search",
                headers= {
                    "Authorization": f"Bearer {get_access_token()}",
                    "Content-Type": "application/json",
                },
                json={**filter_groups, **params},
            )

            # Raise exception for error status codes
            response.raise_for_status()

            data = response.json()

            # Process the results
            tickets = []
            for ticket in data.get("results", []):
                processed_ticket = {
                    "id": ticket["id"],
                    "properties": ticket["properties"],
                    "created_at": parser.isoparse(
                        ticket["properties"]["createdate"]
                    ).isoformat(),
                }

                tickets.append(processed_ticket)

            return {
                "status": "success",
                "tickets": tickets,
                "total": data.get("total", 0),
                "paging": data.get("paging", {}),
            }

        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching HubSpot tickets: {str(e)}"
            if hasattr(e, "response") and hasattr(e.response, "json"):
                error_details = e.response.json()
                error_message += f" - Details: {error_details}"

            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"status": "failed", "error": error_message}