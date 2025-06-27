import os
import requests
from typing import Dict, Any,Optional,TypedDict,List
from ..connection import get_access_token
from urllib.parse import urlparse


class HubSpotResponse(TypedDict):
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class HubSpotClient:
    def __init__(self):
        self.access_token = get_access_token()
        self.base_url = "https://api.hubapi.com"


    """Create a company in HubSpot using the provided properties."""
    def create_company(self, properties: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a company in HubSpot using the provided properties.
        """
        endpoint = f"{self.base_url}/crm/v3/objects/companies"
        access_token = get_access_token()
        headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

        payload = {"properties": properties}

        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    

    """Delete a company from HubSpot by its ID."""
    def delete_company(self, company_id: str) -> HubSpotResponse:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Make the DELETE request to the HubSpot API
            response = requests.delete(endpoint, headers=headers, timeout=10)

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
                        "company_id": company_id,
                    },
                )
                return {"result": None, "error": error_message}

            # If successful, log the response and return success
            print(
                f"Successfully deleted company with ID: {company_id}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            return {
                "result": {
                    "message": f"Successfully deleted company with ID: {company_id}"
                },
                "error": None,
            }

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
            return {"result": None, "error": error_message}

    """Get details of a company by its ID."""    
    
    def get_company_details(self, company_id: str) -> Dict[str, Any]:
        try:
            # Requesting maximum available properties
            properties = [
                "name",
                "domain",
                "createdate",
                "hs_object_id",
                "hs_lastmodifieddate",
                "industry",
                "annualrevenue",
                "numberofemployees",
                "phone",
                "address",
                "city",
                "state",
                "zip",
                "lifecyclestage",
                "hubspot_owner_id",
                "linkedin_company_page",
                "twitterhandle",
                "description",
            ]
            properties_param = "&properties=" + "&properties=".join(properties)

            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}?archived=false{properties_param}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()

            company_data = response.json()
            print(
                f"Successfully retrieved details for company ID {company_id}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            return {"result": company_data, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(
                error_message,
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "status_code": getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None,
                },
            )
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            print(
                f"Error fetching company details: {error_message}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )
            return {"result": None, "error": error_message}
        
    
    """Get filtered companies based on various criteria."""
    def get_filtered_companies(
        self,
        company_ids: Optional[List[str]] = None,
        created_after: str = "",
        created_before: str = "",
        limit: int = 100,
    ) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/search"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            filters = []

            if company_ids:
                filters.append(
                    {
                        "propertyName": "hs_object_id",
                        "operator": "IN",
                        "values": company_ids,
                    }
                )

            if created_after:
                filters.append(
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": created_after,
                    }
                )

            if created_before:
                filters.append(
                    {
                        "propertyName": "createdate",
                        "operator": "LTE",
                        "value": created_before,
                    }
                )

            payload = {
                "filterGroups": [{"filters": filters}],
                "limit": limit,
            }

            response = requests.post(
                endpoint, headers=headers, json=payload, timeout=10
            )
            response.raise_for_status()

            companies = response.json().get("results", [])
            print(
                f"Successfully retrieved {len(companies)} companies",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            return {"result": companies, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(
                error_message,
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "status_code": getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None,
                },
            )
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            print(
                f"Error fetching companies: {error_message}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )
            return {"result": None, "error": error_message} 
        
    """Validate industry value against a predefined set of valid industries."""
    VALID_INDUSTRIES = {
        "ACCOUNTING",
        "AGRICULTURE",
        "APPAREL",
        "BANKING",
        "BIOTECHNOLOGY",
        "CHEMICALS",
        "COMMUNICATIONS",
        "CONSTRUCTION",
        "CONSULTING",
        "EDUCATION",
        "ELECTRONICS",
        "ENERGY",
        "ENGINEERING",
        "ENTERTAINMENT",
        "ENVIRONMENTAL",
        "FINANCE",
        "FOOD & BEVERAGE",
        "GOVERNMENT",
        "HEALTHCARE",
        "HOSPITALITY",
        "INSURANCE",
        "MACHINERY",
        "MANUFACTURING",
        "MEDIA",
        "NOT FOR PROFIT",
        "OTHER",
        "PHARMACEUTICALS",
        "REAL ESTATE",
        "RETAIL",
        "SHIPPING",
        "SOFTWARE",
        "SPORTS",
        "TECHNOLOGY",
        "TELECOMMUNICATIONS",
        "TRANSPORTATION",
        "UTILITIES",
        "RECREATION",
    }

    def validate_industry(self, industry: str) -> str:
        normalized = industry.upper().strip()

        # Log the validation attempt
        print(
            f"Validating industry value",
            extra={
                "path": os.getenv("WM_JOB_PATH"),
                "original_value": industry,
                "normalized_value": normalized,
                "is_valid": normalized in self.VALID_INDUSTRIES,
            },
        )

        if normalized not in self.VALID_INDUSTRIES:
            closest_matches = [v for v in self.VALID_INDUSTRIES if normalized in v]
            error_msg = f"Invalid industry value: '{industry}'. "
            if closest_matches:
                error_msg += f"Did you mean one of these? {', '.join(closest_matches)}"
            else:
                error_msg += (
                    f"Valid values are: {', '.join(sorted(self.VALID_INDUSTRIES))}"
                )
            raise ValueError(error_msg)

        return normalized


    """Update a company's details in HubSpot."""
    def update_company(
        self,
        company_id: str,
        name: str = "",
        domain: str = "",
        industry: str = "",
        phone: str = "",
        address: str = "",
        city: str = "",
        state: str = "",
        country: str = "",
        zip_code: str = "",
        description: str = "",
        employee_count: Optional[int] = None,
        revenue: Optional[float] = None,
        linkedin_url: str = "",
        twitter_handle: str = "",
        website_url: str = "",
    ) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Construct the payload dynamically
            properties = {}
            if name:
                properties["name"] = name
            if domain:
                properties["domain"] = domain
            if industry:
                try:
                    properties["industry"] = self.validate_industry(industry)
                except ValueError as e:
                    return {"result": None, "error": str(e)}
            if phone:
                properties["phone"] = phone
            if address:
                properties["address"] = address
            if city:
                properties["city"] = city
            if state:
                properties["state"] = state
            if country:
                properties["country"] = country
            if zip_code:
                properties["zip"] = zip_code
            if description:
                properties["description"] = description
            if employee_count is not None:
                properties["numberofemployees"] = str(employee_count)
            if revenue is not None:
                properties["annualrevenue"] = str(revenue)
            if linkedin_url:
                properties["linkedin_company_page"] = linkedin_url
            if twitter_handle:
                properties["twitterhandle"] = twitter_handle
            if website_url:
                properties["website"] = website_url

            # If no properties to update, return early
            if not properties:
                return {"result": None, "error": "No fields provided for update"}

            payload = {"properties": properties}

            # Log the request payload for debugging
            print(
                "Sending update request to HubSpot",
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "company_id": company_id,
                    "payload": payload,
                },
            )

            response = requests.patch(
                endpoint, json=payload, headers=headers, timeout=10
            )

            # Log the full response content in case of error
            if not response.ok:
                error_content = response.text
                error_message = f"API request failed: {response.status_code} {response.reason} for url: {response.url}"
                print(
                    error_message,
                    extra={
                        "path": os.getenv("WM_JOB_PATH"),
                        "company_id": company_id,
                        "response_content": error_content,
                        "request_payload": payload,
                    },
                )
                return {
                    "result": None,
                    "error": error_message,
                    "details": error_content,
                }

            updated_company = response.json()
            print(
                f"Successfully updated company {company_id}",
                extra={"path": os.getenv("WM_JOB_PATH"), "updated_fields": properties},
            )

            return {"result": updated_company, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(
                error_message,
                extra={"path": os.getenv("WM_JOB_PATH"), "company_id": company_id},
            )
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(
                error_message,
                extra={"path": os.getenv("WM_JOB_PATH"), "company_id": company_id},
            )
            return {"result": None, "error": error_message}
        
    """Search for a company by its domain."""

    def search_company_by_domain(self, domain: str, limit: int = 10) -> Dict[str, Any]:
        try:
            # Normalize domain (remove "www." if present)
            domain = self._normalize_domain(domain)

            endpoint = f"{self.base_url}/crm/v3/objects/companies/search"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "domain",
                                "operator": "EQ",
                                "value": domain,
                            }
                        ]
                    }
                ],
                "properties": [
                    "name",
                    "domain",
                    "industry",
                    "createdate",
                    "hs_lastmodifieddate",
                ],
                "limit": limit,
            }

            response = requests.post(endpoint, headers=headers, json=payload)

            if response.status_code != 200:
                error_message = f"API request failed: {response.status_code} {response.text}"
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

    def _normalize_domain(self, domain: str) -> str:
        parsed_url = urlparse(domain)
        domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
        return domain.lstrip("www.") if domain.startswith("www.") else domain
    
    """Get recently created or updated companies."""

    def get_recent_companies(
        self, sort_by: str = "createdate", limit: int = 10
    ) -> Dict[str, Any]:
        try:
            if sort_by not in ["createdate", "hs_lastmodifieddate"]:
                return {
                    "result": None,
                    "error": "Invalid sort_by value. Use 'createdate' or 'hs_lastmodifieddate'.",
                }

            endpoint = f"{self.base_url}/crm/v3/objects/companies"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            params = {
                "limit": limit,
                "properties": "name,domain,industry,createdate,hs_lastmodifieddate",
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
        

    def get_all_companies(self) -> Dict[str, Any]:
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies"
            access_token = get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()

            companies = response.json().get("results", [])
            print(
                f"Successfully retrieved {len(companies)} companies",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )

            return {"result": companies, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            print(
                error_message,
                extra={
                    "path": os.getenv("WM_JOB_PATH"),
                    "status_code": getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None,
                },
            )
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            print(
                f"Error fetching companies: {error_message}",
                extra={"path": os.getenv("WM_JOB_PATH")},
            )
            return {"result": None, "error": error_message}


def create_company(
    hubspot_client: HubSpotClient,
    company_name: str,
    domain: str = "",
    description: str = "",
    phone: str = "",
    website: str = "",
) -> Dict[str, Any]:
    try:
        # Only include non-empty properties
        company_properties = {"name": company_name}

        if domain:
            company_properties["domain"] = domain
        if description:
            company_properties["description"] = description
        if phone:
            company_properties["phone"] = phone
        if website:
            company_properties["website"] = website

        api_response = hubspot_client.create_company(company_properties)
        print(f"Successfully created company: {api_response.get('id')}")
        return {"result": api_response, "error": None}
    except Exception as e:
        error_message = f"An error occurred while creating the company: {str(e)}"
        print(error_message, extra={"path": os.getenv("WM_JOB_PATH")})
        return {"result": None, "error": error_message}