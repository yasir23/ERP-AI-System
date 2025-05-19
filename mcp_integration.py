from agents import MCPServerStdio, MCPServerSse
import json
import os
from load_env import get_env

async def setup_database_mcp(schema_name="public"):
    """Set up MCP server for database connection with enhanced ERP capabilities"""
    # Create a configuration file for the database MCP server
    db_config = {
        "connection_string": get_env("ERP_DB_CONNECTION", "postgresql://user:pass@localhost:5432/erp"),
        "allowed_tables": [
            # Finance tables
            "accounts", "transactions", "financial_periods", "tax_rates", "currencies",
            # Inventory tables
            "inventory", "products", "warehouses", "stock_movements", "purchase_orders",
            # Sales tables
            "customers", "sales_orders", "invoices", "payments", "shipping",
            # HR tables
            "employees", "departments", "positions", "payroll", "attendance"
        ],
        "allowed_schemas": [schema_name],
        "max_results": int(get_env("MCP_DB_MAX_RESULTS", "1000")),
        "enable_write": get_env("MCP_DB_ENABLE_WRITE", "true").lower() == "true",  # Allow write operations for full ERP functionality
        "query_timeout_ms": int(get_env("MCP_DB_QUERY_TIMEOUT", "5000")),
        "allowed_functions": [
            # Aggregate functions
            "sum", "avg", "count", "min", "max",
            # ERP-specific functions
            "calculate_inventory_value", "calculate_order_total", "get_account_balance"
        ]
    }
    
    # Write configuration to a temporary file
    config_path = "erp_database_config.json"
    with open(config_path, "w") as f:
        json.dump(db_config, f)
    
    # Connect to the MCP server
    try:
        server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-database", config_path],
            }
        )
        return server
    except Exception as e:
        print(f"Error setting up database MCP server: {e}")
        return None

# Define standard SQL queries as MCP tools for common ERP operations
async def add_sql_query_tools(mcp_tools):
    """Add predefined SQL query tools for common ERP operations"""
    erp_queries = {
        "get_low_stock_items": {
            "description": "Get inventory items that are below reorder point",
            "query": "SELECT * FROM inventory WHERE quantity < reorder_point"
        },
        "get_overdue_invoices": {
            "description": "Get list of overdue invoices",
            "query": "SELECT * FROM invoices WHERE due_date < CURRENT_DATE AND status != 'paid'"
        },
        "get_top_customers": {
            "description": "Get top customers by sales volume",
            "query": "SELECT customer_id, SUM(total_amount) as total FROM sales_orders GROUP BY customer_id ORDER BY total DESC LIMIT 10"
        },
        "get_monthly_sales": {
            "description": "Get monthly sales report",
            "query": "SELECT DATE_TRUNC('month', order_date) as month, SUM(total_amount) as total FROM sales_orders GROUP BY month ORDER BY month"
        }
    }
    
    # These would be added to the tools if we had a real MCP server for SQL queries
    # Since this is a mock implementation, we're just illustrating what's possible
    return mcp_tools

async def setup_api_mcp():
    """Set up MCP server for external API connection"""
    # Create a configuration file for the API MCP server
    api_config = {
        "base_url": get_env("ERP_API_URL", "https://api.example.com/erp"),
        "auth": {
            "type": "bearer",
            "token": get_env("ERP_API_TOKEN", "")
        },
        "endpoints": [
            {
                "name": "getCustomerData",
                "path": "/customers/{customer_id}",
                "method": "GET"
            },
            {
                "name": "createOrder",
                "path": "/orders",
                "method": "POST"
            },
            {
                "name": "updateInventory",
                "path": "/inventory/{item_id}",
                "method": "PUT"
            },
            {
                "name": "processPayment",
                "path": "/payments",
                "method": "POST"
            },
            {
                "name": "generateInvoice",
                "path": "/invoices",
                "method": "POST"
            }
        ]
    }
    
    # Write configuration to a temporary file
    config_path = "erp_api_config.json"
    with open(config_path, "w") as f:
        json.dump(api_config, f)
    
    # Connect to the MCP server
    try:
        server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-api", config_path],
            }
        )
        return server
    except Exception as e:
        print(f"Error setting up API MCP server: {e}")
        return None

async def setup_mcp_tools():
    """Set up all MCP servers and return their tools"""
    tools = []
    
    # Setup database MCP
    db_server = await setup_database_mcp()
    if db_server:
        async with db_server as server:
            db_tools = await server.list_tools()
            tools.extend(db_tools)
            # Add pre-defined SQL query tools
            tools = await add_sql_query_tools(tools)
    
    # Setup API MCP
    api_server = await setup_api_mcp()
    if api_server:
        async with api_server as server:
            api_tools = await server.list_tools()
            tools.extend(api_tools)
    
    return tools 