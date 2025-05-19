import agents
import inspect
from typing import Dict, Any

# Print available methods related to tools
print("=== Available Tool Functions ===")
tool_functions = [name for name in dir(agents) if "tool" in name.lower()]
print(tool_functions)

# Define a simple function for testing
def simple_function(param1: str) -> Dict[str, Any]:
    """
    A simple function to test with FunctionTool.
    
    Args:
        param1: A test parameter
        
    Returns:
        A dictionary with the result
    """
    return {"result": f"You said: {param1}"}

# Attempt to create a function tool using different methods
print("\n=== FunctionTool Class ===")
print(inspect.signature(agents.FunctionTool.__init__))

print("\n=== Testing Tool Creation ===")
try:
    # Try using the tool module
    print("Testing agents.tool.function...")
    if hasattr(agents.tool, "function"):
        tool1 = agents.tool.function(simple_function)
        print(f"SUCCESS: Created tool with agents.tool.function: {tool1}")
except Exception as e:
    print(f"ERROR: {e}")

try:
    # Try using function_tool
    print("\nTesting agents.function_tool...")
    if hasattr(agents, "function_tool"):
        tool2 = agents.function_tool(simple_function)
        print(f"SUCCESS: Created tool with agents.function_tool: {tool2}")
except Exception as e:
    print(f"ERROR: {e}")

try:
    # Try using Tool.function
    print("\nTesting agents.Tool.function...")
    if hasattr(agents.Tool, "function"):
        tool3 = agents.Tool.function(simple_function)
        print(f"SUCCESS: Created tool with agents.Tool.function: {tool3}")
except Exception as e:
    print(f"ERROR: {e}")

# Print the module structure
print("\n=== Module Structure ===")
if hasattr(agents, "tool"):
    print(f"agents.tool dir: {dir(agents.tool)}") 