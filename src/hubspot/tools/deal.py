import os
import requests
from typing import TypedDict,Dict,Optional,Any,List
from datetime import datetime ,timezone
from ..connection import get_access_token



class HubSpotAssociationType(TypedDict):
    associationCategory: str
    associationTypeId: int

class HubSpotAssociation(TypedDict):
    to: Dict[str, str]
    types: List[HubSpotAssociationType]


class HubSpotResponse(TypedDict):
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class HubSpotProperties(TypedDict, total=False):
    dealname: str
    pipeline: str
    dealstage: str
    amount: str
    closedate: str
    dealtype: str
    hubspot_owner_id: str


class HubSpotClient:

    def __init__(self):
        self.access_token = get_access_token()
        self.base_url = "https://api.hubapi.com"

    def _create_association(
        self, entity_id: str, association_type_id: int
    ) -> HubSpotAssociation:
        return {
            "to": {"id": entity_id},
            "types": [
                {
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": association_type_id,
                }
            ],
        }

    def create_deal(
        self,
        deal_name: str,
        pipeline: str,
        deal_stage: str,
        amount: Optional[float] = None,
        close_date: str = "",
        deal_type: str = "",
        owner_id: str = "",
        associated_company_id: str = "",
        associated_contact_ids: List[str] = [],
        custom_properties: Dict[str, str] = {},
    ) -> HubSpotResponse:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Initialize properties with required fields
            properties: HubSpotProperties = {
                "dealname": deal_name,
                "pipeline": pipeline,
                "dealstage": deal_stage,
            }

            # Add optional properties if provided
            if amount is not None:
                properties["amount"] = str(amount)

            if close_date:
                # Convert ISO 8601 date format to milliseconds epoch time
                try:
                    dt = datetime.strptime(close_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    properties["closedate"] = str(
                        int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
                    )
                except ValueError as e:
                    return {"result": None, "error": f"Invalid date format: {str(e)}"}

            if deal_type:
                properties["dealtype"] = deal_type
            if owner_id:
                properties["hubspot_owner_id"] = owner_id

            # Add custom properties if provided
            if custom_properties:
                if not isinstance(custom_properties, dict):
                    return {
                        "result": None,
                        "error": f"custom_properties must be a dictionary. Received type: {type(custom_properties)}",
                    }
                properties.update(custom_properties)

            payload: Dict[str, Any] = {"properties": properties}

            # Handle associations
            associations: List[HubSpotAssociation] = []
            if associated_company_id:
                associations.append(self._create_association(associated_company_id, 5))
            if associated_contact_ids:
                associations.extend(
                    [
                        self._create_association(contact_id, 3)
                        for contact_id in associated_contact_ids
                    ]
                )

            if associations:
                payload["associations"] = associations

            # Log the request payload
            print(
                "Sending create deal request to HubSpot",
                extra={"path": os.getenv("WM_JOB_PATH"), "payload": payload},
            )

            # Make the API request
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=10
            )

            if not response.ok:
                error_content = response.text
                error_message = (
                    f"API request failed: {response.status_code} "
                    f"{response.reason} for url: {response.url}. "
                    f"Details: {error_content}"
                )
                print(
                    error_message,
                    extra={
                        "path": os.getenv("WM_JOB_PATH"),
                        "response_content": error_content,
                        "request_payload": payload,
                    },
                )
                return {"result": None, "error": error_message}

            created_deal = response.json()
            print(
                f"Successfully created deal '{deal_name}'",
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "deal_id": created_deal.get("id"),
                },
            )

            return {"result": created_deal, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}


    def update_deal(
        self,
        deal_id: str,
        deal_name: str = "",
        amount: str = "",
        pipeline: str = "",
        deal_stage: str = "",
        close_date: str = "",
        description: str = "",
        hubspot_owner_id: str = "",
    ) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Prepare the update payload
            properties = {}
            if deal_name:
                properties["dealname"] = deal_name
            if amount:
                properties["amount"] = amount
            if pipeline:
                properties["pipeline"] = pipeline
            if deal_stage:
                properties["dealstage"] = deal_stage
            if close_date:
                properties["closedate"] = close_date
            if description:
                properties["description"] = description
            if hubspot_owner_id:
                properties["hubspot_owner_id"] = hubspot_owner_id

            # Automatically set updatedAt field
            properties["hs_lastmodifieddate"] = datetime.utcnow().isoformat() + "Z"

            payload = {"properties": properties}
            response = requests.patch(endpoint, headers=headers, json=payload)

            if not response.ok:
                error_message = f"API request failed: {response.status_code} {response.reason}. Details: {response.text}"
                print(
                    error_message,
                    extra={
                        "path": os.getenv("WM_JOB_PATH"),
                        "response_content": response.text,
                    },
                )
                return {"result": None, "error": error_message}

            return {"result": response.json(), "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}


    def search_deals(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals/search"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Create multiple filters to search across different fields
            filters = [
                {
                    "filterGroups": [
                        {
                            "filters": [
                                {
                                    "propertyName": "dealname",
                                    "operator": "CONTAINS_TOKEN",
                                    "value": query
                                }
                            ]
                        },
                        {
                            "filters": [
                                {
                                    "propertyName": "pipeline",
                                    "operator": "CONTAINS_TOKEN",
                                    "value": query
                                }
                            ]
                        },
                        {
                            "filters": [
                                {
                                    "propertyName": "dealstage",
                                    "operator": "CONTAINS_TOKEN",
                                    "value": query
                                }
                            ]
                        }
                    ]
                }
            ]

            payload = {
                "filterGroups": filters,
                "properties": [
                    "dealname",
                    "amount",
                    "pipeline",
                    "dealstage",
                    "createdate",
                    "hs_lastmodifieddate",
                    "hubspot_owner_id",
                    "closedate"
                ],
                "limit": limit,
                "sorts": [
                    {
                        "propertyName": "createdate",
                        "direction": "DESCENDING"
                    }
                ]
            }

            response = requests.post(endpoint, headers=headers, json=payload)

            if response.status_code != 200:
                error_message = (
                    f"API request failed: {response.status_code} {response.text}"
                )
                print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                return {"result": None, "error": error_message}

            data = response.json()
            return {"result": data.get("results", []), "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
    

    def get_deal_pipelines(self) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/pipelines/deals"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Make the API request
            response = requests.get(endpoint, headers=headers, timeout=10)

            if not response.ok:
                error_content = response.text
                error_message = (
                    f"API request failed: {response.status_code} "
                    f"{response.reason} for url: {response.url}. "
                    f"Details: {error_content}"
                )
                print(
                    error_message,
                    extra={
                        "path": os.getenv("WM_JOB_PATH"),
                        "response_content": error_content,
                    },
                )
                return {"result": None, "error": error_message}

            pipelines = response.json()
            print(
                "Successfully fetched HubSpot deal pipelines",
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "pipelines_count": len(pipelines.get("results", [])),
                },
            )

            return {"result": pipelines, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}   

    
    def get_deal_by_id(self, deal_id: str) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            params = {
                "properties": "dealname,amount,closedate,createdate,pipeline,dealstage,hubspot_owner_id,description"
            }

            response = requests.get(endpoint, headers=headers, params=params)
            if not response.ok:
                error_message = f"API request failed: {response.status_code} {response.reason} - {response.text}"
                print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                return {"result": None, "error": error_message}

            return {"result": response.json(), "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}  

    
    def get_all_deals(self) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Initialize parameters for pagination
            params = {
                "limit": 100,  # Maximum results per page
                "properties": "dealname,amount,closedate,pipeline,dealstage",  # Specify deal properties to fetch
            }

            deals = []
            while True:
                response = requests.get(endpoint, headers=headers, params=params)
                if not response.ok:
                    error_message = f"API request failed: {response.status_code} {response.reason} for url: {response.url}. Details: {response.text}"
                    print(
                        error_message,
                        extra={"path": os.getenv("WM_JOB_PATH"), "response_content": response.text},
                    )
                    return {"result": None, "error": error_message}

                data = response.json()

                # Append the deals from this page to the results list
                deals.extend(data.get("results", []))

                # Check if there is another page of results
                if "paging" in data and "next" in data["paging"]:
                    params["after"] = data["paging"]["next"]["after"]
                else:
                    break  # No more pages, exit the loop

            return {"result": deals, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}   

    
    def get_deals_by_filters(
        self,
        pipeline: str = "",
        deal_stage: str = "",
        start_date: str = "",
        end_date: str = "",
        closedate_start: str = "",
        closedate_end: str = "",
        limit: int = 100,
    ) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals/search"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Build filter groups for the search criteria
            filter_groups = []
            filters = []

            if pipeline:
                filters.append(
                    {"propertyName": "pipeline", "operator": "EQ", "value": pipeline}
                )

            if deal_stage:
                filters.append(
                    {"propertyName": "dealstage", "operator": "EQ", "value": deal_stage}
                )

            if start_date and end_date:
                filters.append(
                    {
                        "propertyName": "createdate",
                        "operator": "BETWEEN",
                        "value": start_date,
                        "highValue": end_date,
                    }
                )

            if closedate_start and closedate_end:
                filters.append(
                    {
                        "propertyName": "closedate",
                        "operator": "BETWEEN",
                        "value": closedate_start,
                        "highValue": closedate_end,
                    }
                )

            if filters:
                filter_groups.append({"filters": filters})

            # Build the search request payload
            payload = {
                "filterGroups": filter_groups,
                "properties": [
                    "dealname",
                    "amount",
                    "closedate",
                    "createdate",
                    "pipeline",
                    "dealstage",
                    "hubspot_owner_id",
                ],
                "limit": limit,
            }

            deals = []
            after = None

            while True:
                if after:
                    payload["after"] = after

                response = requests.post(endpoint, headers=headers, json=payload)

                if not response.ok:
                    error_message = f"API request failed: {response.status_code} {response.reason} for url: {response.url}. Details: {response.text}"
                    print(
                        error_message,
                        extra={
                            "path": os.getenv("WM_JOB_PATH"),
                            "response_content": response.text,
                        },
                    )
                    return {"result": None, "error": error_message}

                data = response.json()
                deals.extend(data.get("results", []))

                # Check for pagination
                if "paging" in data and "next" in data["paging"]:
                    after = data["paging"]["next"]["after"]
                else:
                    break

            return {"result": deals, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
        

    
    def get_recent_deals(
        self, sort_by: str = "createdate", limit: int = 10
    ) -> Dict[str, Any]:
        try:
            # TODO: Use "createdate" to fetch newly created deals and "hs_lastmodifieddate"
            #       to fetch recently updated deals. Ensure the correct sort_by value is passed.

            if sort_by not in ["createdate", "hs_lastmodifieddate"]:
                return {
                    "result": None,
                    "error": "Invalid sort_by value. Use 'createdate' or 'hs_lastmodifieddate'.",
                }

            endpoint = f"{self.base_url}/crm/v3/objects/deals"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            params = {
                "limit": limit,
                "properties": "dealname,amount,pipeline,dealstage,createdate,hs_lastmodifieddate",
                "sort": f"-{sort_by}",  # Sort in descending order (most recent first)
            }

            response = requests.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                error_message = (
                    f"API request failed: {response.status_code} {response.text}"
                )
                print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
                return {"result": None, "error": error_message}

            data = response.json()
            return {"result": data.get("results", []), "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}
        
    
    def delete_deal(self, deal_id: str) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.delete(endpoint, headers=headers)

            if response.status_code == 204:
                return {
                    "result": f"Successfully deleted deal with ID: {deal_id}",
                    "error": None,
                }
            else:
                error_message = (
                    f"Failed to delete deal: {response.status_code} {response.text}"
                )
                print(
                    error_message,
                    extra={"path": os.getenv("WM_JOB_PATH"), "deal_id": deal_id},
                )
                return {"result": None, "error": error_message}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}    
    