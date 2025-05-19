from typing import List, Dict, Optional, Any
from models import FinancialTransaction, InventoryItem, SalesOrder, EmployeeRecord, CustomerInfo

# ===== FINANCE TOOLS =====
def get_account_balance(account_code: str) -> Dict[str, Any]:
    """Get current balance of a specific account"""
    # Mock implementation
    return {"account_code": account_code, "balance": 10000.0, "currency": "USD"}

def record_transaction(transaction: FinancialTransaction) -> Dict[str, Any]:
    """Record a financial transaction in the system"""
    # Mock implementation
    return {"status": "success", "transaction_id": transaction.transaction_id}

def generate_financial_report(report_type: str, start_date: str, end_date: str) -> str:
    """Generate financial reports (income statement, balance sheet, cash flow)"""
    # Mock implementation
    return f"Financial report of type {report_type} for period {start_date} to {end_date} generated"

# ===== INVENTORY TOOLS =====
def check_inventory_levels(item_id: Optional[str] = None) -> List[InventoryItem]:
    """Get inventory levels, optionally filtered by item_id"""
    # Mock implementation
    items = [
        InventoryItem(item_id="ITM001", name="Laptop", quantity=15, reorder_point=10, unit_cost=1200.0),
        InventoryItem(item_id="ITM002", name="Mouse", quantity=5, reorder_point=20, unit_cost=25.0)
    ]
    if item_id:
        return [item for item in items if item.item_id == item_id]
    return items

def create_purchase_order(items: List[Dict[str, int]]) -> Dict[str, Any]:
    """Create a purchase order for specified items and quantities"""
    # Mock implementation
    order_id = "PO-12345"
    return {"status": "success", "order_id": order_id, "message": "Purchase order created successfully"}

def receive_inventory(purchase_order_id: str, items_received: List[Dict[str, int]]) -> Dict[str, Any]:
    """Record receipt of inventory against a purchase order"""
    # Mock implementation
    return {"status": "success", "purchase_order_id": purchase_order_id, "message": "Inventory received"}

# ===== SALES TOOLS =====
def get_customer_info(customer_id: str) -> CustomerInfo:
    """Retrieve customer information by ID"""
    # Mock implementation
    return CustomerInfo(
        customer_id=customer_id,
        name="Acme Corp",
        email="contact@acmecorp.com",
        phone="555-123-4567",
        address="123 Business St, Commerce City"
    )

def create_sales_order(order: SalesOrder) -> Dict[str, Any]:
    """Create a new sales order in the system"""
    # Mock implementation
    return {"status": "success", "order_id": order.order_id, "message": "Sales order created successfully"}

def process_sales_order(order_id: str) -> Dict[str, Any]:
    """Process a sales order (check inventory, reserve items, generate invoice)"""
    # Mock implementation
    return {"status": "success", "order_id": order_id, "message": "Order processed successfully"}

# ===== HR TOOLS =====
def get_employee_data(employee_id: str) -> EmployeeRecord:
    """Retrieve employee data by ID"""
    # Mock implementation
    return EmployeeRecord(
        employee_id=employee_id,
        name="John Doe",
        department="IT",
        position="Developer",
        salary=85000.0
    )

def update_employee_info(employee_id: str, field: str, value: Any) -> Dict[str, Any]:
    """Update a specific field of employee information"""
    # Mock implementation
    return {"status": "success", "employee_id": employee_id, "message": f"Updated {field} successfully"}

def process_payroll(department: Optional[str] = None) -> Dict[str, Any]:
    """Process payroll for all employees or a specific department"""
    # Mock implementation
    if department:
        return {"status": "success", "message": f"Payroll processed for department: {department}"}
    return {"status": "success", "message": "Payroll processed for all employees"} 