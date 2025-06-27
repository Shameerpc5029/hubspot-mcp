# 🚀 Quick Start Guide

Welcome to the HubSpot MCP Server! This guide will get you up and running in just a few minutes.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Claude Desktop** application installed
- **HubSpot Developer Account** (free)
- **Nango Integration** configured (for secure authentication)

## ⚡ 5-Minute Setup

### Step 1: Get HubSpot Access Token

1. **Visit** [HubSpot Developer Portal](https://developers.hubspot.com/)
2. **Sign in** with your HubSpot account
3. **Create a new app** or select existing one
4. **Go to** the "Auth" tab → "Scopes"
5. **Enable these scopes**:
   ```
   ✅ crm.objects.companies.read
   ✅ crm.objects.companies.write  
   ✅ crm.objects.contacts.read
   ✅ crm.objects.contacts.write
   ✅ crm.lists.read
   ✅ crm.lists.write
   ```
6. **Copy your access token** from the "Auth" tab

### Step 2: Configure Nango Integration

Obtain your Nango credentials:
- **NANGO_BASE_URL**: Your Nango instance base URL
- **NANGO_SECRET_KEY**: Your Nango secret key
- **NANGO_CONNECTION_ID**: Your connection identifier
- **NANGO_INTEGRATION_ID**: Your integration identifier

### Step 3: Configure Claude Desktop

**Add this configuration** to your Claude Desktop config file:

#### macOS:
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Windows:
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uvx",
      "args": ["git+https://github.com/Shameerpc5029/hubspot-mcp.git"],
      "env": {
        "NANGO_BASE_URL": "enter_your_nango_base_url_here",
        "NANGO_SECRET_KEY": "enter_your_nango_secret_key_here",
        "NANGO_CONNECTION_ID": "enter_your_nango_connection_id_here",
        "NANGO_INTEGRATION_ID": "enter_your_nango_integration_id_here"
      }
    }
  }
}
```

**Important**: Replace the placeholder values with your actual Nango credentials:
- Replace `enter_your_nango_base_url_here` with your Nango base URL
- Replace `enter_your_nango_secret_key_here` with your secret key
- Replace `enter_your_nango_connection_id_here` with your connection ID
- Replace `enter_your_nango_integration_id_here` with your integration ID

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

## ✅ Testing Your Setup

In Claude, try these commands:

1. **Test connection**: *"List all companies in my HubSpot"*
2. **Create a test company**: *"Create a company called Test Corp with domain test.com"*
3. **Search for contacts**: *"Find all contacts with gmail email addresses"*

## 🎯 What You Can Do Now

### Company Management
- Create, update, delete companies
- Search by domain or other criteria
- Get recent company activity
- Bulk operations with filters

### Contact Management  
- Create, update, delete contacts
- Search by email, name, phone
- Manage list memberships
- Track recent contact activity

### Natural Language Examples
- *"Create a company for Acme Corp with their website acme.com"*
- *"Find the contact john@example.com and update their phone number"*
- *"Show me all companies created this month"*
- *"Add contact ID 12345 to my VIP customers list"*

## 🔧 Troubleshooting

### Common Issues

**❌ "Tool not found" errors**
- Restart Claude Desktop after configuration changes
- Verify your Nango credentials are correct
- Check that `uvx` is installed on your system

**❌ Authentication failures**  
- Double-check your Nango credentials in the config
- Ensure all required scopes are enabled in your HubSpot app
- Verify your Nango integration is properly configured

**❌ uvx command not found**
- Install uvx: `pip install uvx` or `pipx install uvx`
- Ensure uvx is in your system PATH

### Test Connection
You can test your setup by asking Claude simple questions like:
```
"Can you connect to my HubSpot account?"
"Show me my recent contacts"
"List my companies"
```

### Debug Mode
If you encounter issues, check the Claude Desktop logs or console for error messages.

## 📞 Getting Help

- **Documentation**: See the main [README.md](README.md) for detailed info
- **Issues**: Report problems on [GitHub Issues](https://github.com/Shameerpc5029/hubspot-mcp/issues)
- **HubSpot API**: Check [HubSpot Developer Docs](https://developers.hubspot.com/docs/api/overview)

## 🎉 You're Ready!

You now have HubSpot CRM integrated with Claude! Start with simple commands and explore the powerful automation possibilities.

**Key Features Available:**
- 🏢 Complete company management
- 👥 Contact creation and updates
- 📋 List management
- 🔍 Advanced search capabilities
- 📊 Recent activity tracking

**Happy automating! 🚀**