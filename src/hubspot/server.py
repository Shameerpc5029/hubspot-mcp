"""
HubSpot MCP Server - A Model Context Protocol server for HubSpot CRM integration.

This server provides tools for managing companies and contacts in HubSpot CRM via the HubSpot API.
It implements the MCP stdio transport protocol for seamless integration with MCP clients.
"""

import json
import logging
from typing import Any, Dict, List
import asyncio
import sys
from datetime import datetime
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the HubSpot client and tools
from .tools.company import HubSpotClient, create_company
from .tools.contact import (
    HubSpotListManager,
    HubSpotContactDeleter,
    HubSpotContactUpdater,
    HubSpotContactSearcher,
    HubSpotContactGetter,
    HubSpotRecentContactsGetter,
    HubSpotContactCreator
)


class HubSpotMCPServer:
    """MCP Server for HubSpot CRM integration using proper MCP patterns."""
    
    def __init__(self):
        """Initialize the HubSpot MCP server with all tools."""
        self.server = Server("hubspot-mcp")
        
        # Initialize clients lazily to avoid authentication errors during startup
        self._hubspot_client = None
        self._list_manager = None
        self._contact_deleter = None
        self._contact_updater = None
        self._contact_searcher = None
        self._contact_getter = None
        self._recent_contacts_getter = None
        self._contact_creator = None
        
        self._setup_tools()
        logger.info("HubSpot MCP Server initialized successfully")

    @property
    def hubspot_client(self):
        """Lazy initialization of HubSpot client."""
        if self._hubspot_client is None:
            self._hubspot_client = HubSpotClient()
        return self._hubspot_client

    @property
    def list_manager(self):
        """Lazy initialization of list manager."""
        if self._list_manager is None:
            self._list_manager = HubSpotListManager()
        return self._list_manager

    @property
    def contact_deleter(self):
        """Lazy initialization of contact deleter."""
        if self._contact_deleter is None:
            self._contact_deleter = HubSpotContactDeleter()
        return self._contact_deleter

    @property
    def contact_updater(self):
        """Lazy initialization of contact updater."""
        if self._contact_updater is None:
            self._contact_updater = HubSpotContactUpdater()
        return self._contact_updater

    @property
    def contact_searcher(self):
        """Lazy initialization of contact searcher."""
        if self._contact_searcher is None:
            self._contact_searcher = HubSpotContactSearcher()
        return self._contact_searcher

    @property
    def contact_getter(self):
        """Lazy initialization of contact getter."""
        if self._contact_getter is None:
            self._contact_getter = HubSpotContactGetter()
        return self._contact_getter

    @property
    def recent_contacts_getter(self):
        """Lazy initialization of recent contacts getter."""
        if self._recent_contacts_getter is None:
            self._recent_contacts_getter = HubSpotRecentContactsGetter()
        return self._recent_contacts_getter

    @property
    def contact_creator(self):
        """Lazy initialization of contact creator."""
        if self._contact_creator is None:
            self._contact_creator = HubSpotContactCreator()
        return self._contact_creator
    
    def _setup_tools(self):
        """Setup all available tools with their schemas."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="create_company",
                    description="Create a new company in HubSpot CRM with specified properties",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_name": {"type": "string", "description": "Name of the company (required)"},
                            "domain": {"type": "string", "description": "Company domain/website"},
                            "description": {"type": "string", "description": "Company description"},
                            "phone": {"type": "string", "description": "Company phone number"},
                            "website": {"type": "string", "description": "Company website URL"}
                        },
                        "required": ["company_name"]
                    }
                ),
                Tool(
                    name="get_company_details",
                    description="Get detailed information about a specific company by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "string", "description": "Unique identifier of the company"}
                        },
                        "required": ["company_id"]
                    }
                ),
                Tool(
                    name="update_company",
                    description="Update an existing company's information in HubSpot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "string", "description": "Unique identifier of the company"},
                            "name": {"type": "string", "description": "Company name"},
                            "domain": {"type": "string", "description": "Company domain"},
                            "industry": {"type": "string", "description": "Industry classification"},
                            "phone": {"type": "string", "description": "Phone number"},
                            "address": {"type": "string", "description": "Street address"},
                            "city": {"type": "string", "description": "City"},
                            "state": {"type": "string", "description": "State/province"},
                            "country": {"type": "string", "description": "Country"},
                            "zip_code": {"type": "string", "description": "ZIP/postal code"},
                            "description": {"type": "string", "description": "Company description"},
                            "employee_count": {"type": "integer", "description": "Number of employees"},
                            "revenue": {"type": "number", "description": "Annual revenue"},
                            "linkedin_url": {"type": "string", "description": "LinkedIn company page URL"},
                            "twitter_handle": {"type": "string", "description": "Twitter handle"},
                            "website_url": {"type": "string", "description": "Website URL"}
                        },
                        "required": ["company_id"]
                    }
                ),
                Tool(
                    name="delete_company",
                    description="Delete a company from HubSpot CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "string", "description": "Unique identifier of the company to delete"}
                        },
                        "required": ["company_id"]
                    }
                ),
                Tool(
                    name="get_all_companies",
                    description="Retrieve all companies from HubSpot CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_filtered_companies",
                    description="Get companies based on various filter criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_ids": {
                                "type": "array", 
                                "items": {"type": "string"}, 
                                "description": "List of company IDs to filter by"
                            },
                            "created_after": {"type": "string", "description": "Filter companies created after this date (ISO format)"},
                            "created_before": {"type": "string", "description": "Filter companies created before this date (ISO format)"},
                            "limit": {"type": "integer", "default": 100, "description": "Maximum number of companies to return"}
                        }
                    }
                ),
                Tool(
                    name="search_company_by_domain",
                    description="Search for companies by their domain name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string", "description": "Domain name to search for"},
                            "limit": {"type": "integer", "default": 10, "description": "Maximum number of results to return"}
                        },
                        "required": ["domain"]
                    }
                ),
                Tool(
                    name="get_recent_companies",
                    description="Get recently created or updated companies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sort_by": {
                                "type": "string", 
                                "enum": ["createdate", "hs_lastmodifieddate"], 
                                "default": "createdate",
                                "description": "Sort by creation date or last modified date"
                            },
                            "limit": {"type": "integer", "default": 10, "description": "Maximum number of companies to return"}
                        }
                    }
                ),
                # Contact Management Tools
                Tool(
                    name="create_contact",
                    description="Create a new contact in HubSpot CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Contact's email address (required)"},
                            "first_name": {"type": "string", "description": "Contact's first name"},
                            "last_name": {"type": "string", "description": "Contact's last name"},
                            "phone": {"type": "string", "description": "Contact's phone number (optional)"}
                        },
                        "required": ["email", "first_name", "last_name"]
                    }
                ),
                Tool(
                    name="get_contact_by_email",
                    description="Retrieve a contact from HubSpot using their email address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Contact's email address to search for"}
                        },
                        "required": ["email"]
                    }
                ),
                Tool(
                    name="update_contact_by_email",
                    description="Update a contact in HubSpot using their email address as identifier",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Contact's email address to update"},
                            "properties": {
                                "type": "object", 
                                "description": "Dictionary of properties to update",
                                "additionalProperties": True
                            }
                        },
                        "required": ["email", "properties"]
                    }
                ),
                Tool(
                    name="delete_contact_by_id",
                    description="Delete a contact from HubSpot using their contact ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contact_id": {"type": "string", "description": "HubSpot contact ID to delete"}
                        },
                        "required": ["contact_id"]
                    }
                ),
                Tool(
                    name="delete_contact_by_email",
                    description="Delete a contact from HubSpot using their email address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Contact's email address to delete"}
                        },
                        "required": ["email"]
                    }
                ),
                Tool(
                    name="search_contacts",
                    description="Search for contacts in HubSpot using provided filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Email to search for (optional)"},
                            "firstname": {"type": "string", "description": "First name to search for (optional)"},
                            "phone": {"type": "string", "description": "Phone number to search for (optional)"},
                            "limit": {"type": "integer", "default": 100, "description": "Maximum number of contacts to return"}
                        }
                    }
                ),
                Tool(
                    name="get_all_contacts",
                    description="Retrieve all contacts from HubSpot CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_recent_contacts",
                    description="Retrieve recently created or updated contacts from HubSpot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "since": {"type": "string", "description": "ISO datetime string for filtering contacts modified after this time (optional)"},
                            "limit": {"type": "integer", "default": 10, "description": "Maximum number of contacts to return"}
                        }
                    }
                ),
                Tool(
                    name="add_contact_to_list",
                    description="Add a contact to a HubSpot static list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "list_id": {"type": "string", "description": "The ID of the HubSpot list"},
                            "contact_id": {"type": "string", "description": "The ID of the contact to be added"}
                        },
                        "required": ["list_id", "contact_id"]
                    }
                ),
                Tool(
                    name="remove_contact_from_list",
                    description="Remove a contact from a HubSpot static list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "list_id": {"type": "string", "description": "The ID of the HubSpot list"},
                            "contact_id": {"type": "string", "description": "The ID of the contact to be removed"}
                        },
                        "required": ["list_id", "contact_id"]
                    }
                )                

            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a tool with the given arguments."""
            try:
                logger.info(f"Executing tool: {name} with arguments: {arguments}")
                
                # Route the tool call to the appropriate function
                if name == "create_company":
                    result = self._create_company(**arguments)
                elif name == "get_company_details":
                    result = self.hubspot_client.get_company_details(**arguments)
                elif name == "update_company":
                    result = self.hubspot_client.update_company(**arguments)
                elif name == "delete_company":
                    result = self.hubspot_client.delete_company(**arguments)
                elif name == "get_all_companies":
                    result = self.hubspot_client.get_all_companies(**arguments)
                elif name == "get_filtered_companies":
                    result = self.hubspot_client.get_filtered_companies(**arguments)
                elif name == "search_company_by_domain":
                    result = self.hubspot_client.search_company_by_domain(**arguments)
                elif name == "get_recent_companies":
                    result = self.hubspot_client.get_recent_companies(**arguments)
                # Contact tools    
                elif name == "create_contact":
                    result = self.contact_creator.create_contact(**arguments)
                elif name == "get_contact_by_email":
                    result = self.contact_getter.get_contact_by_email(**arguments)
                elif name == "update_contact_by_email":
                    result = self.contact_updater.update_contact_by_email(**arguments)
                elif name == "delete_contact_by_id":
                    result = self.contact_deleter.delete_contact_by_id(**arguments)
                elif name == "delete_contact_by_email":
                    result = self.contact_deleter.delete_contact_by_email(**arguments)
                elif name == "search_contacts":
                    result = self.contact_searcher.search_contacts(**arguments)
                elif name == "get_all_contacts":
                    result = self.hubspot_client.get_all_contacts()
                elif name == "get_recent_contacts":
                    # Handle datetime conversion if provided
                    if 'since' in arguments and arguments['since']:
                        try:
                            arguments['since'] = datetime.fromisoformat(arguments['since'].replace('Z', '+00:00'))
                        except ValueError:
                            # If parsing fails, remove the since parameter
                            del arguments['since']
                    result = self.recent_contacts_getter.get_recent_contacts(**arguments)
                elif name == "add_contact_to_list":
                    result = self.list_manager.add_contact_to_list(**arguments)
                elif name == "remove_contact_from_list":
                    result = self.list_manager.remove_contact_from_list(**arguments)    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                logger.info(f"Tool {name} executed successfully")
                # Return the result as TextContent
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
            except Exception as e:
                # Return error information
                error_result = {
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
                logger.error(f"Tool {name} execution failed: {str(e)}")
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    def _create_company(self, **kwargs) -> Dict[str, Any]:
        """Wrapper for the create_company function to match the expected signature."""
        try:
            # Import the create_company function from the client module
            return create_company(self.hubspot_client, **kwargs)
        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            return {"result": None, "error": str(e)}
    
    async def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting HubSpot MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for the MCP server."""
    

    # Create and run the server
    server = HubSpotMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
