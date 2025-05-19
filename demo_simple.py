import asyncio
import os
from agents import Agent, Runner, FunctionTool
from load_env import load_env_file, check_required_vars, get_env

# Sample data (in-memory instead of using PostgreSQL)
SAMPLE_INVENTORY = [
    {"item_id": "ITM001", "name": "Laptop", "quantity": 15, "reorder_point": 10, "unit_cost": 1200.0},
    {"item_id": "ITM002", "name": "Mouse", "quantity": 5, "reorder_point": 20, "unit_cost": 20.0}
]

SAMPLE_EMPLOYEES = [
    {"employee_id": "EMP001", "name": "John Doe", "department": "IT", "position": "Developer", "salary": 85000.0},
    {"employee_id": "EMP002", "name": "Jane Smith", "department": "Sales", "position": "Sales Manager", "salary": 90000.0}
]

SAMPLE_CUSTOMERS = [
    {"customer_id": "CUST001", "name": "Acme Corp", "email": "contact@acmecorp.com", "phone": "555-123-4567"},
    {"customer_id": "CUST002", "name": "TechStart Inc", "email": "info@techstart.com", "phone": "555-987-6543"}
]

# Function tools
def check_inventory(item_id=None):
    """Get inventory levels, optionally filtered by item_id"""
    if item_id:
        items = [item for item in SAMPLE_INVENTORY if item["item_id"] == item_id]
        return items if items else {"error": f"Item {item_id} not found"}
    return SAMPLE_INVENTORY

def get_employee_data(employee_id):
    """Retrieve employee data by ID"""
    employees = [emp for emp in SAMPLE_EMPLOYEES if emp["employee_id"] == employee_id]
    if not employees:
        return {"error": f"Employee {employee_id} not found"}
    return employees[0]

def get_customer_info(customer_id):
    """Retrieve customer information by ID"""
    customers = [cust for cust in SAMPLE_CUSTOMERS if cust["customer_id"] == customer_id]
    if not customers:
        return {"error": f"Customer {customer_id} not found"}
    return customers[0]

def create_purchase_order(items):
    """Create a purchase order for specified items and quantities"""
    # Mock implementation
    order_id = "PO-12345"
    return {"status": "success", "order_id": order_id, "message": "Purchase order created successfully", "items": items}

def process_payroll(department=None):
    """Process payroll for all employees or a specific department"""
    if department:
        employees = [emp for emp in SAMPLE_EMPLOYEES if emp["department"] == department]
        if not employees:
            return {"error": f"No employees found in department {department}"}
        return {"status": "success", "message": f"Payroll processed for department: {department}", "employees": len(employees)}
    
    return {"status": "success", "message": "Payroll processed for all employees", "employees": len(SAMPLE_EMPLOYEES)}

async def main():
    """Main entry point for the simple ERP demo"""
    # Load environment variables from .env file
    load_env_file()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY"]
    if not check_required_vars(required_vars):
        return
    
    # Create function tools
    tools = [
        FunctionTool(
            function=check_inventory,
            description="Check current inventory levels for a product"
        ),
        FunctionTool(
            function=get_employee_data,
            description="Get information about an employee"
        ),
        FunctionTool(
            function=get_customer_info,
            description="Get information about a customer"
        ),
        FunctionTool(
            function=create_purchase_order,
            description="Create a purchase order for inventory"
        ),
        FunctionTool(
            function=process_payroll,
            description="Process payroll for employees"
        )
    ]
    
    # Create a simple agent with the tools
    agent = Agent(
        name="ERP Assistant",
        instructions="""You are an ERP system assistant that can help with inventory management, 
        employee data, customer information, purchase orders, and payroll processing.
        
        Available data:
        - Inventory items: Laptops (ITM001) and Mice (ITM002)
        - Employees: John Doe (EMP001) in IT and Jane Smith (EMP002) in Sales
        - Customers: Acme Corp (CUST001) and TechStart Inc (CUST002)
        
        Use the appropriate tools to help users with their ERP-related queries.""",
        tools=tools
    )
    
    # Set up runner
    runner = Runner()
    
    # Interactive shell
    print("\n=== Simple ERP Demo ===")
    print("Type 'exit' to quit\n")
    print("Example queries:")
    print("- Check inventory for laptops")
    print("- Get employee data for EMP001")
    print("- Get customer info for Acme Corp")
    print("- Create a purchase order for 5 laptops")
    print("- Process payroll for the IT department\n")
    
    while True:
        # Get user input
        user_input = input("\nERP Request: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # Process the request
        print("\nProcessing request...")
        try:
            result = await runner.run(agent, user_input)
            print("\nResponse:")
            print(result.final_output)
        except Exception as e:
            print(f"Error processing request: {e}")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 