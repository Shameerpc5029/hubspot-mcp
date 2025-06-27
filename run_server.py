#!/usr/bin/env python3
"""
Entry point for the HubSpot MCP Server.
This script can be run directly to start the server in stdio mode.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from hubspot.server import main
    main()
