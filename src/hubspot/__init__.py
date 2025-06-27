"""
HubSpot MCP Server - A Model Context Protocol server for HubSpot CRM integration.
"""

from .server import HubSpotMCPServer, main
from .connection import get_access_token, get_connection_credentials

__version__ = "0.1.0"
__all__ = ['HubSpotMCPServer', 'main', 'get_access_token', 'get_connection_credentials']
