from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# ERP DATA MODELS
class FinancialTransaction(BaseModel):
    transaction_id: str
    amount: float
    account_code: str
    description: str
    date: str

class InventoryItem(BaseModel):
    item_id: str
    name: str
    quantity: int
    reorder_point: int
    unit_cost: float

class SalesOrder(BaseModel):
    order_id: str
    customer_id: str
    items: List[Dict[str, int]]  # item_id: quantity
    status: str = "draft"
    total_amount: Optional[float] = None

class EmployeeRecord(BaseModel):
    employee_id: str
    name: str
    department: str
    position: str
    salary: float

class CustomerInfo(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    address: str 