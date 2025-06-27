import logging
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any,List
from ..connection import get_access_token   
logger = logging.getLogger(__name__)
class HubSpotClient:
    def __init__(self, ):
        self.access_token = get_access_token()
        self.base_url = "https://api.hubapi.com"
        logger.info("HubSpotClient initialized", extra={"path": os.getenv("WM_JOB_PATH")})

    def get_engagement(self, engagement_id: str) -> Dict[str, Any]:
        try:
            if not engagement_id:
                raise ValueError("Engagement ID is required")

            logger.info("Fetching full engagement details", extra={
                "engagement_id": engagement_id,
                "path": os.getenv("WM_JOB_PATH"),
            })

            url = f"{self.base_url}/crm/v3/objects/engagements/{engagement_id}?properties=hs_engagement_type,hs_createdate,hs_lastmodifieddate,associations"
            access_token = get_access_token()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=headers)
            response_data = response.json()

            if response.status_code not in (200, 201):
                error_message = f"API request failed: {response.status_code} {response_data.get('message', response.text)}"
                logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                return {"result": None, "error": error_message}

            # Extract engagement details
            properties = response_data.get("properties", {})
            associations = response_data.get("associations", {})

            result = {
                "id": response_data.get("id"),
                "properties": properties,
                "associations": associations,
                "hs_engagement_type": properties.get("hs_engagement_type", "UNKNOWN"),
                "created_at": properties.get("hs_createdate"),
                "last_modified": properties.get("hs_lastmodifieddate"),
            }

            return {"result": result, "error": None}

        except Exception as e:
            error_message = f"Error fetching engagement: {str(e)}"
            logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
        
    def create_engagement(
        self,
        engagement_type: str,
        contact_ids: List[str] = [],
        company_id: str = "",
        deal_id: str = "",
        subject: str = "",
        body: str = "",
        status: str = "",
        start_time: str = "",
        end_time: str = "",
        task_type: str = "",
    ) -> Dict[str, Any]:
        """
        Create an engagement in HubSpot.
        """
        try:
            if not engagement_type:
                raise ValueError("engagement_type is required")

            object_type_map = {
                "TASK": "tasks",
                "CALL": "calls",
                "EMAIL": "emails",
                "MEETING": "meetings",
                "NOTE": "notes",
            }

            object_type = object_type_map.get(engagement_type.upper())
            if not object_type:
                raise ValueError(f"Invalid engagement type: {engagement_type}")

            # Define association labels based on HubSpot's standard associations
            associations = []
            if contact_ids:
                for cid in contact_ids:
                    if cid:
                        associations.append(
                            {
                                "from": {"id": cid},
                                "to": {
                                    "id": "0"
                                },  # Will be replaced with created engagement ID
                                "type": "contact_to_engagement",
                            }
                        )
            if company_id:
                associations.append(
                    {
                        "from": {"id": company_id},
                        "to": {
                            "id": "0"
                        },  # Will be replaced with created engagement ID
                        "type": "company_to_engagement",
                    }
                )
            if deal_id:
                associations.append(
                    {
                        "from": {"id": deal_id},
                        "to": {
                            "id": "0"
                        },  # Will be replaced with created engagement ID
                        "type": "deal_to_engagement",
                    }
                )

            # Set default times for meetings
            if object_type == "meetings" and not start_time:
                start_time = datetime.utcnow().isoformat() + "Z"
            if object_type == "meetings" and not end_time:
                end_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"

            # Build properties based on object type
            properties = {
                "hs_timestamp": start_time
                if start_time
                else datetime.utcnow().isoformat() + "Z",
            }

            if object_type == "tasks":
                properties.update(
                    {
                        "hs_task_subject": subject,
                        "hs_task_body": body,
                        "hs_task_status": status or "NOT_STARTED",
                        "hs_task_type": task_type,
                    }
                )
            elif object_type == "notes":
                properties.update({"hs_note_body": body})
            elif object_type == "calls":
                properties.update(
                    {
                        "hs_call_title": subject,
                        "hs_call_body": body,
                        "hs_call_status": status,
                    }
                )
            elif object_type == "meetings":
                properties.update(
                    {
                        "hs_meeting_title": subject or "Meeting",
                        "hs_meeting_body": body,
                        "hs_meeting_start_time": start_time,
                        "hs_meeting_end_time": end_time,
                        "hs_meeting_location": "Virtual Meeting",
                        "hs_meeting_outcome": "SCHEDULED",
                    }
                )

            # Remove None values from properties
            properties = {k: v for k, v in properties.items() if v is not None}

            # First create the engagement
            create_payload = {
                "properties": properties,
            }

            endpoint = f"{self.base_url}/crm/v3/objects/{object_type}"
            access_token = get_access_token()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            logger.info(
                f"Creating {object_type} with payload: {create_payload}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            # Create the engagement first
            response = requests.post(endpoint, headers=headers, json=create_payload)
            response_data = response.json()

            if response.status_code not in (200, 201):
                error_message = f"API request failed: {response.status_code} {response_data.get('message', response.text)}"
                logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                return {"result": None, "error": error_message}

            # Get the created engagement ID
            engagement_id = response_data.get("id")

            # If we have associations to create, create them now
            if associations and engagement_id:
                for assoc in associations:
                    assoc["to"]["id"] = engagement_id
                    assoc_endpoint = f"{self.base_url}/crm/v4/associations/{object_type}/batch/create"
                    assoc_payload = {"inputs": [assoc]}

                    assoc_response = requests.post(
                        assoc_endpoint, headers=headers, json=assoc_payload
                    )
                    if assoc_response.status_code not in (200, 201):
                        logger.info(
                            f"Failed to create association: {assoc_response.status_code} {assoc_response.text}",
                            extra={"path": os.getenv("WM_JOB_PATH")},
                        )


            return {"result": response_data, "error": None}

        except Exception as e:
            error_message = f"Error creating engagement: {str(e)}"
            logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
    
    
    def delete_engagement(self, engagement_id: str) -> Dict[str, Any]:
        try:
            if not engagement_id:
                raise ValueError("Engagement ID is required")

            logger.info(
                f"Deleting engagement: {engagement_id}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            url = f"{self.base_url}/engagements/v1/engagements/{engagement_id}"
            access_token = get_access_token()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                return {
                    "result": f"Engagement {engagement_id} deleted successfully",
                    "error": None,
                }

            response_data = response.json()
            error_message = response_data.get("message", response.text)
            logger.info(
                f"Failed to delete engagement: {error_message}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Error deleting engagement: {str(e)}"
            logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
    
    def get_engagements(self) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/engagements"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            params = {"limit": 100}
            all_engagements = []
            
            while endpoint:
                response = requests.get(endpoint, headers=headers, params=params)
                response_data = response.json()

                if response.status_code != 200:
                    error_message = f"Failed to fetch engagements: {response.status_code} {response_data.get('message', response.text)}"
                    logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                    return {"result": None, "error": error_message}

                all_engagements.extend(response_data.get("results", []))
                endpoint = response_data.get("paging", {}).get("next", {}).get("link")

            return {"result": all_engagements, "error": None}

        except Exception as e:
            error_message = f"Error fetching engagements: {str(e)}"
            logger.info(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}    
    
        