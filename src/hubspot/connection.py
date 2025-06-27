import os
import logging
from typing import Any
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

def get_connection_credentials() -> dict[str, Any]:
    """Get credentials from Nango"""
    connection_id = os.environ.get("NANGO_CONNECTION_ID")
    integration_id = os.environ.get("NANGO_INTEGRATION_ID")
    base_url = os.environ.get("NANGO_BASE_URL")
    secret_key = os.environ.get("NANGO_SECRET_KEY")
    
    if not all([connection_id, integration_id, base_url, secret_key]):
        missing_vars = []
        if not connection_id:
            missing_vars.append("NANGO_CONNECTION_ID")
        if not integration_id:
            missing_vars.append("NANGO_INTEGRATION_ID")
        if not base_url:
            missing_vars.append("NANGO_BASE_URL")
        if not secret_key:
            missing_vars.append("NANGO_SECRET_KEY")
        
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    url = f"{base_url}/connection/{connection_id}"
    params = {
        "provider_config_key": integration_id,
        "refresh_token": "true",
    }
    headers = {"Authorization": f"Bearer {secret_key}"}
    
    try:
        logger.info(f"Requesting connection credentials from Nango: {url}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        logger.info("Successfully retrieved connection credentials from Nango")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get connection credentials from Nango: {str(e)}")
        raise ValueError(f"Failed to get connection credentials from Nango: {str(e)}")

def get_access_token() -> str:
    """Get access token from Nango credentials"""
    try:
        credentials = get_connection_credentials()
        access_token = credentials.get("credentials", {}).get("access_token")
        if not access_token:
            raise ValueError("Access token not found in credentials response")
        logger.info("Successfully retrieved access token from Nango")
        return access_token
    except Exception as e:
        # For development/testing, you might want to fall back to a direct token
        direct_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if direct_token:
            logger.warning("Using direct HubSpot access token instead of Nango credentials")
            return direct_token
        logger.error(f"Failed to get access token: {str(e)}")
        raise ValueError(f"Failed to get access token: {str(e)}")
