# server.py
import sys
from mcp.server.fastmcp import FastMCP
from voltage_payments_api import VoltagePaymentsAPI

try:
    # Create an MCP server
    print("Creating MCP server...", file=sys.stderr)
    mcp = FastMCP("Demo")

    # Initialize the Voltage Payments API client
    voltage_api = VoltagePaymentsAPI()

    # Add a tool to get all wallets
    @mcp.tool()
    def get_all_wallets() -> list:
        """Get all wallets for the organization"""
        print("Getting all wallets...", file=sys.stderr)
        return voltage_api.get_all_wallets()

    # Add an addition tool
    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers"""
        print(f"Adding {a} + {b}", file=sys.stderr)
        return a + b

    # Add a dynamic greeting resource
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        print(f"Greeting {name}", file=sys.stderr)
        return f"Hello, {name}!"

    print("Server setup complete, ready to run", file=sys.stderr)
except Exception as e:
    print(f"Error setting up server: {e}", file=sys.stderr)
    raise