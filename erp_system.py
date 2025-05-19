import asyncio
import os
import sys
from agents import Runner
from agents import create_coordinator_agent
from mcp_integration import setup_mcp_tools
from load_env import load_env_file, check_required_vars, get_env

async def main():
    """
    Main entry point for the ERP Agent System
    """
    # Load environment variables from .env file
    load_env_file()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "ERP_DB_CONNECTION"]
    if not check_required_vars(required_vars):
        return
    
    # Set up MCP tools if needed
    try:
        print("Setting up MCP integration...")
        mcp_tools = await setup_mcp_tools()
        print(f"Successfully set up {len(mcp_tools)} MCP tools")
    except Exception as e:
        print(f"Warning: Error setting up MCP tools: {e}")
        print("Continuing without MCP integration")
        mcp_tools = []
    
    # Create the main coordinator agent
    print("Creating ERP coordinator agent...")
    coordinator = create_coordinator_agent(mcp_tools)
    
    # Set up runner
    runner = Runner()
    
    # Interactive shell
    print("\n=== ERP Agent System ===")
    print("Type 'exit' to quit\n")
    
    while True:
        # Get user input
        user_input = input("\nERP Request: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # Process the request
        print("\nProcessing request...")
        try:
            result = await runner.run(coordinator, user_input)
            print("\nResponse:")
            print(result.final_output)
        except Exception as e:
            print(f"Error processing request: {e}")

if __name__ == "__main__":
    # Check Python version
    import sys
    if sys.version_info < (3, 7):
        print("This application requires Python 3.7 or higher")
        sys.exit(1)
    
    # Run the main function
    asyncio.run(main()) 