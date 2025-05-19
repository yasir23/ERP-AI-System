from agents import Agent, FunctionTool
from tools import (
    get_account_balance, record_transaction, generate_financial_report,
    check_inventory_levels, create_purchase_order, receive_inventory,
    get_customer_info, create_sales_order, process_sales_order,
    get_employee_data, update_employee_info, process_payroll
)
from guardrails import FinanceGuardrail, HRGuardrail, SecurityGuardrail

# Finance Agent
def create_finance_agent():
    finance_tools = [
        FunctionTool(
            function=get_account_balance,
            description="Get the current balance of a financial account"
        ),
        FunctionTool(
            function=record_transaction,
            description="Record a financial transaction in the system"
        ),
        FunctionTool(
            function=generate_financial_report,
            description="Generate a financial report for a specified period"
        )
    ]

    return Agent(
        name="Finance Agent",
        instructions="""You are a specialized finance agent for an ERP system.
You have access to financial data and can process transactions, check balances, and generate reports.
Always ensure compliance with accounting principles and financial regulations.
For complex analyses, collect all relevant data before making conclusions.
When handling financial data, always verify account codes and transaction amounts.""",
        tools=finance_tools,
        guardrails=[FinanceGuardrail(), SecurityGuardrail()]
    )

# Inventory Agent
def create_inventory_agent():
    inventory_tools = [
        FunctionTool(
            function=check_inventory_levels,
            description="Check current inventory levels for a product"
        ),
        FunctionTool(
            function=create_purchase_order,
            description="Create a purchase order for inventory"
        ),
        FunctionTool(
            function=receive_inventory,
            description="Record receipt of inventory items"
        )
    ]

    return Agent(
        name="Inventory Agent",
        instructions="""You are a specialized inventory management agent for an ERP system.
You monitor stock levels, suggest reorders, and optimize inventory.
When checking inventory, always verify if items are below reorder points.
For purchase orders, prioritize items below reorder threshold.
When receiving inventory, validate quantities against purchase orders.
Always calculate total costs for purchase decisions.""",
        tools=inventory_tools,
        guardrails=[SecurityGuardrail()]
    )

# Sales Agent
def create_sales_agent():
    sales_tools = [
        FunctionTool(
            function=get_customer_info,
            description="Get information about a customer"
        ),
        FunctionTool(
            function=create_sales_order,
            description="Create a new sales order"
        ),
        FunctionTool(
            function=process_sales_order,
            description="Process and fulfill a sales order"
        ),
        FunctionTool(
            function=check_inventory_levels,
            description="Check current inventory levels for a product"
        )
    ]

    return Agent(
        name="Sales Agent",
        instructions="""You are a specialized sales agent for an ERP system.
You handle customer interactions, create and process sales orders, and check product availability.
Always verify inventory levels before confirming orders.
For new orders, collect all necessary customer information.
Calculate accurate totals for all orders.
Provide estimated delivery dates based on inventory status.""",
        tools=sales_tools,
        guardrails=[SecurityGuardrail()]
    )

# HR Agent
def create_hr_agent():
    hr_tools = [
        FunctionTool(
            function=get_employee_data,
            description="Get information about an employee"
        ),
        FunctionTool(
            function=update_employee_info,
            description="Update employee information"
        ),
        FunctionTool(
            function=process_payroll,
            description="Process payroll for employees"
        )
    ]

    return Agent(
        name="HR Agent",
        instructions="""You are a specialized human resources agent for an ERP system.
You manage employee data, process payroll, and handle HR-related requests.
Maintain strict confidentiality for all employee information.
For payroll processing, verify all calculations before submission.
When updating employee records, confirm the changes before committing.
Always follow company policies and legal requirements for HR operations.""",
        tools=hr_tools,
        guardrails=[HRGuardrail(), SecurityGuardrail()]
    )

# Coordinator Agent (Main ERP agent)
def create_coordinator_agent(mcp_tools=None):
    # Create specialized agents
    finance_agent = create_finance_agent()
    inventory_agent = create_inventory_agent()
    sales_agent = create_sales_agent()
    hr_agent = create_hr_agent()
    
    # Tools for the coordinator
    coordinator_tools = [
        finance_agent.as_tool(),
        inventory_agent.as_tool(),
        sales_agent.as_tool(),
        hr_agent.as_tool()
    ]
    
    # Add MCP tools if provided
    if mcp_tools:
        coordinator_tools.extend(mcp_tools)
    
    return Agent(
        name="ERP Coordinator",
        instructions="""You are the main coordinator for an ERP system.
Your job is to understand user requests and delegate to specialized agents:
- Finance Agent: For financial transactions, account queries, and financial reports
- Inventory Agent: For inventory management, purchase orders, and stock level monitoring
- Sales Agent: For customer interactions, sales orders, and order processing
- HR Agent: For employee data, payroll, and HR management

Determine which specialized agent is most appropriate for each task and delegate accordingly.
For complex queries that span multiple domains, coordinate between multiple agents to fulfill the request.
Always prioritize data security and compliance with business rules.""",
        tools=coordinator_tools,
        guardrails=[SecurityGuardrail()]
    ) 