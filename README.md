# HubSpot MCP Server

A Model Context Protocol (MCP) server for HubSpot CRM integration, providing tools for managing companies and contacts through the HubSpot API.

## Features

### Company Management
- Create new companies
- Get company details by ID
- Update company information
- Delete companies
- Search companies by domain
- Get all companies
- Filter companies by various criteria
- Get recently created/updated companies

### Contact Management
- Create new contacts
- Get contact details by email
- Update contact information
- Delete contacts (by ID or email)
- Search contacts with filters
- Get all contacts
- Get recently created/updated contacts
- Add/remove contacts from lists

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hubspot-mcp
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or if using uv:
```bash
uv sync
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Option 1: Using Nango (Recommended for production)
```env
NANGO_CONNECTION_ID=your_connection_id
NANGO_INTEGRATION_ID=your_integration_id
NANGO_BASE_URL=https://auth-dev.assistents.ai
NANGO_SECRET_KEY=your_secret_key
HUBSPOT_BASE_URL=https://api.hubapi.com
```

#### Option 2: Direct HubSpot Access Token (Development/Testing)
```env
HUBSPOT_ACCESS_TOKEN=your_direct_access_token
HUBSPOT_BASE_URL=https://api.hubapi.com
```

### Getting HubSpot Access Token

1. Go to [HubSpot Developer Portal](https://developers.hubspot.com/)
2. Create a new app or use an existing one
3. Configure the required scopes:
   - `crm.objects.companies.read`
   - `crm.objects.companies.write`
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.lists.read`
   - `crm.lists.write`
4. Get your access token from the app settings

## Usage

### Running the Server

#### Method 1: Direct Script
```bash
python main.py
```

#### Method 2: Python Module
```bash
python -m src.hubspot.server
```

#### Method 3: With Virtual Environment
```bash
source .venv/bin/activate
python -m hubspot.server
```

### MCP Client Integration

The server communicates via stdin/stdout using the MCP protocol. Configure your MCP client to use this server:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "python",
      "args": ["/path/to/hubspot-mcp/main.py"]
    }
  }
}
```

## Available Tools

### Company Tools

1. **create_company** - Create a new company
   - `company_name` (required): Name of the company
   - `domain`: Company domain/website
   - `description`: Company description
   - `phone`: Company phone number
   - `website`: Company website URL

2. **get_company_details** - Get company information by ID
   - `company_id` (required): Unique identifier of the company

3. **update_company** - Update company information
   - `company_id` (required): Unique identifier of the company
   - Various optional fields for updating

4. **delete_company** - Delete a company
   - `company_id` (required): Unique identifier of the company

5. **get_all_companies** - Retrieve all companies

6. **get_filtered_companies** - Get companies with filters
   - `company_ids`: List of company IDs
   - `created_after`: Filter by creation date
   - `created_before`: Filter by creation date
   - `limit`: Maximum number of results

7. **search_company_by_domain** - Search companies by domain
   - `domain` (required): Domain name to search
   - `limit`: Maximum number of results

8. **get_recent_companies** - Get recently created/updated companies
   - `sort_by`: Sort by creation or modification date
   - `limit`: Maximum number of results

### Contact Tools

1. **create_contact** - Create a new contact
   - `email` (required): Contact's email address
   - `first_name` (required): Contact's first name
   - `last_name` (required): Contact's last name
   - `phone`: Contact's phone number (optional)

2. **get_contact_by_email** - Get contact by email
   - `email` (required): Contact's email address

3. **update_contact_by_email** - Update contact information
   - `email` (required): Contact's email address
   - `properties` (required): Dictionary of properties to update

4. **delete_contact_by_id** - Delete contact by ID
   - `contact_id` (required): HubSpot contact ID

5. **delete_contact_by_email** - Delete contact by email
   - `email` (required): Contact's email address

6. **search_contacts** - Search contacts with filters
   - `email`: Email to search for
   - `firstname`: First name to search for
   - `phone`: Phone number to search for
   - `limit`: Maximum number of results

7. **get_all_contacts** - Retrieve all contacts

8. **get_recent_contacts** - Get recently created/updated contacts
   - `since`: ISO datetime string for filtering
   - `limit`: Maximum number of results

9. **add_contact_to_list** - Add contact to a list
   - `list_id` (required): HubSpot list ID
   - `contact_id` (required): HubSpot contact ID

10. **remove_contact_from_list** - Remove contact from a list
    - `list_id` (required): HubSpot list ID
    - `contact_id` (required): HubSpot contact ID

## Error Handling

The server includes comprehensive error handling:
- API request failures are caught and returned as error responses
- Missing environment variables are validated at startup
- Invalid parameters are validated before API calls
- Network timeouts and connection errors are handled gracefully

## Development

### Project Structure
```
hubspot-mcp/
├── src/
│   └── hubspot/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── connection.py      # Authentication and connection handling
│       └── tools/
│           ├── __init__.py
│           ├── company.py     # Company management tools
│           └── contact.py     # Contact management tools
├── run_server.py             # Entry point script
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── .env                     # Environment variables
└── README.md
```

### Adding New Tools

1. Create a new tool class in the appropriate module
2. Add the tool schema to the `list_tools()` function in `server.py`
3. Add the tool handler to the `call_tool()` function in `server.py`
4. Update the imports in `__init__.py` files

### Testing

You can test individual tools by running the server and sending MCP protocol messages, or by importing the classes directly for unit testing.

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all required environment variables are set in `.env`
   - Check that the `.env` file is in the project root

2. **Authentication Errors**
   - Verify your HubSpot access token is valid
   - Check that the required scopes are configured for your HubSpot app
   - Ensure Nango credentials are correct (if using Nango)

3. **API Rate Limits**
   - HubSpot has API rate limits that may cause temporary failures
   - The server will return appropriate error messages for rate limit issues

4. **Connection Issues**
   - Verify network connectivity to HubSpot API
   - Check firewall settings if running in a restricted environment

### Debug Mode

You can enable debug logging by setting the `DEBUG` environment variable:
```bash
export DEBUG=1
python run_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.
