import os
import logging
import requests
from typing import Dict, Any, Optional
from ..connection import get_access_token
from urllib.parse import urlparse

# Set up logging
logger = logging.getLogger(__name__)

class HubSpotResponse(Dict[str, Any]):
    pass

class HubSpotClient:
    def __init__(self):
        self.base_url = "https://api.hubapi.com"
        self._access_token = None

    def _get_access_token(self) -> str:
        """Get access token, cached for performance."""
        if self._access_token is None:
            self._access_token = get_access_token()
        return self._access_token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token."""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    def create_company(self, properties: Dict[str, str]) -> Dict[str, Any]:
        """Create a company in HubSpot using the provided properties."""
        endpoint = f"{self.base_url}/crm/v3/objects/companies"
        headers = self._get_headers()
        payload = {"properties": properties}

        logger.info(f"Creating company with properties: {properties}")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Successfully created company with ID: {result.get('id')}")
        return result

    def delete_company(self, company_id: str) -> HubSpotResponse:
        """Delete a company from HubSpot by its ID."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
            headers = self._get_headers()

            logger.info(f"Deleting company with ID: {company_id}")
            response = requests.delete(endpoint, headers=headers, timeout=30)

            if not response.ok:
                error_content = response.text
                error_message = (
                    f"API request failed: {response.status_code} "
                    f"{response.reason} for url: {response.url}. "
                    f"Details: {error_content}"
                )
                logger.error(f"Failed to delete company {company_id}: {error_message}")
                return {"result": None, "error": error_message}

            logger.info(f"Successfully deleted company with ID: {company_id}")
            return {
                "result": {
                    "message": f"Successfully deleted company with ID: {company_id}"
                },
                "error": None,
            }

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while deleting company {company_id}: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error while deleting company {company_id}: {error_message}")
            return {"result": None, "error": error_message}

    def get_company_details(self, company_id: str) -> Dict[str, Any]:
        """Get details of a company by its ID."""
        try:
            properties = [
                "name", "domain", "createdate", "hs_object_id", "hs_lastmodifieddate",
                "industry", "annualrevenue", "numberofemployees", "phone", "address",
                "city", "state", "zip", "lifecyclestage", "hubspot_owner_id",
                "linkedin_company_page", "twitterhandle", "description",
            ]
            properties_param = "&properties=" + "&properties=".join(properties)
            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}?archived=false{properties_param}"
            headers = self._get_headers()

            logger.info(f"Fetching details for company ID: {company_id}")
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            company_data = response.json()
            logger.info(f"Successfully retrieved details for company ID {company_id}")
            return {"result": company_data, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while fetching company {company_id}: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error fetching company details for {company_id}: {error_message}")
            return {"result": None, "error": error_message}

    def get_filtered_companies(
        self,
        company_ids: Optional[list] = None,
        created_after: str = "",
        created_before: str = "",
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get filtered companies based on various criteria."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/search"
            headers = self._get_headers()

            filters = []
            if company_ids:
                filters.append({
                    "propertyName": "hs_object_id",
                    "operator": "IN",
                    "values": company_ids,
                })

            if created_after:
                filters.append({
                    "propertyName": "createdate",
                    "operator": "GTE",
                    "value": created_after,
                })

            if created_before:
                filters.append({
                    "propertyName": "createdate",
                    "operator": "LTE",
                    "value": created_before,
                })

            payload = {
                "filterGroups": [{"filters": filters}],
                "limit": limit,
            }

            logger.info(f"Fetching filtered companies with {len(filters)} filters, limit: {limit}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            companies = response.json().get("results", [])
            logger.info(f"Successfully retrieved {len(companies)} filtered companies")
            return {"result": companies, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while fetching filtered companies: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error fetching filtered companies: {error_message}")
            return {"result": None, "error": error_message}

    VALID_INDUSTRIES = {
        "ACCOUNTING", "AGRICULTURE", "APPAREL", "BANKING", "BIOTECHNOLOGY",
        "CHEMICALS", "COMMUNICATIONS", "CONSTRUCTION", "CONSULTING", "EDUCATION",
        "ELECTRONICS", "ENERGY", "ENGINEERING", "ENTERTAINMENT", "ENVIRONMENTAL",
        "FINANCE", "FOOD & BEVERAGE", "GOVERNMENT", "HEALTHCARE", "HOSPITALITY",
        "INSURANCE", "MACHINERY", "MANUFACTURING", "MEDIA", "NOT FOR PROFIT",
        "OTHER", "PHARMACEUTICALS", "REAL ESTATE", "RETAIL", "SHIPPING",
        "SOFTWARE", "SPORTS", "TECHNOLOGY", "TELECOMMUNICATIONS", "TRANSPORTATION",
        "UTILITIES", "RECREATION",
    }

    def validate_industry(self, industry: str) -> str:
        """Validate industry value against a predefined set of valid industries."""
        normalized = industry.upper().strip()

        logger.debug(f"Validating industry value: {industry} -> {normalized}")

        if normalized not in self.VALID_INDUSTRIES:
            closest_matches = [v for v in self.VALID_INDUSTRIES if normalized in v]
            error_msg = f"Invalid industry value: '{industry}'. "
            if closest_matches:
                error_msg += f"Did you mean one of these? {', '.join(closest_matches)}"
            else:
                error_msg += f"Valid values are: {', '.join(sorted(self.VALID_INDUSTRIES))}"
            logger.error(f"Industry validation failed: {error_msg}")
            raise ValueError(error_msg)

        return normalized

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
        """Update a company's details in HubSpot."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
            headers = self._get_headers()

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
                error_msg = "No fields provided for update"
                logger.warning(f"Update company {company_id}: {error_msg}")
                return {"result": None, "error": error_msg}

            payload = {"properties": properties}

            logger.info(f"Updating company {company_id} with properties: {list(properties.keys())}")

            response = requests.patch(endpoint, json=payload, headers=headers, timeout=30)

            if not response.ok:
                error_content = response.text
                error_message = f"API request failed: {response.status_code} {response.reason} for url: {response.url}"
                logger.error(f"Failed to update company {company_id}: {error_message}, Details: {error_content}")
                return {
                    "result": None,
                    "error": error_message,
                    "details": error_content,
                }

            updated_company = response.json()
            logger.info(f"Successfully updated company {company_id}")
            return {"result": updated_company, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while updating company {company_id}: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error while updating company {company_id}: {error_message}")
            return {"result": None, "error": error_message}

    def search_company_by_domain(self, domain: str, limit: int = 10) -> Dict[str, Any]:
        """Search for a company by its domain."""
        try:
            # Normalize domain (remove "www." if present)
            domain = self._normalize_domain(domain)

            endpoint = f"{self.base_url}/crm/v3/objects/companies/search"
            headers = self._get_headers()

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

            logger.info(f"Searching for companies with domain: {domain}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                error_message = f"API request failed: {response.status_code} {response.text}"
                logger.error(f"Search by domain failed: {error_message}")
                return {"result": None, "error": error_message}

            data = response.json()
            results = data.get("results", [])
            logger.info(f"Found {len(results)} companies with domain: {domain}")
            return {"result": results, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while searching by domain {domain}: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error while searching by domain {domain}: {error_message}")
            return {"result": None, "error": error_message}

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain by removing www. prefix."""
        parsed_url = urlparse(domain)
        domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
        return domain.lstrip("www.") if domain.startswith("www.") else domain

    def get_recent_companies(
        self, sort_by: str = "createdate", limit: int = 10
    ) -> Dict[str, Any]:
        """Get recently created or updated companies."""
        try:
            if sort_by not in ["createdate", "hs_lastmodifieddate"]:
                error_msg = "Invalid sort_by value. Use 'createdate' or 'hs_lastmodifieddate'."
                logger.error(f"Invalid sort_by parameter: {sort_by}")
                return {"result": None, "error": error_msg}

            endpoint = f"{self.base_url}/crm/v3/objects/companies"
            headers = self._get_headers()

            params = {
                "limit": limit,
                "properties": "name,domain,industry,createdate,hs_lastmodifieddate",
                "sort": f"-{sort_by}",  # Sort in descending order (most recent first)
            }

            logger.info(f"Fetching recent companies, sorted by: {sort_by}, limit: {limit}")
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            if response.status_code != 200:
                error_message = f"API request failed: {response.status_code} {response.text}"
                logger.error(f"Get recent companies failed: {error_message}")
                return {"result": None, "error": error_message}

            data = response.json()
            results = data.get("results", [])
            logger.info(f"Successfully retrieved {len(results)} recent companies")
            return {"result": results, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while fetching recent companies: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error while fetching recent companies: {error_message}")
            return {"result": None, "error": error_message}

    def get_all_companies(self) -> Dict[str, Any]:
        """Get all companies from HubSpot."""
        try:
            endpoint = f"{self.base_url}/crm/v3/objects/companies"
            headers = self._get_headers()

            logger.info("Fetching all companies")
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            companies = response.json().get("results", [])
            logger.info(f"Successfully retrieved {len(companies)} companies")
            return {"result": companies, "error": None}

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            logger.error(f"Request exception while fetching all companies: {error_message}")
            return {"result": None, "error": error_message}

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error fetching all companies: {error_message}")
            return {"result": None, "error": error_message}

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
                error_message = f"API request failed: {response.status_code} {response.text}"
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


def create_company(
    hubspot_client: HubSpotClient,
    company_name: str,
    domain: str = "",
    description: str = "",
    phone: str = "",
    website: str = "",
) -> Dict[str, Any]:
    """Create a company using the HubSpot client."""
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

        logger.info(f"Creating company: {company_name}")
        api_response = hubspot_client.create_company(company_properties)
        logger.info(f"Successfully created company: {api_response.get('id')}")
        return {"result": api_response, "error": None}
    except Exception as e:
        error_message = f"An error occurred while creating the company: {str(e)}"
        logger.error(f"Error creating company {company_name}: {error_message}")
        return {"result": None, "error": error_message}
