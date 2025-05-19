-- ERP System PostgreSQL Schema
-- This schema is designed to be used with the MCP integration

-- Create schema
CREATE SCHEMA IF NOT EXISTS erp;

SET search_path TO erp;

-- Finance Tables
CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    amount DECIMAL(15, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_amount CHECK (amount != 0)
);

CREATE TABLE IF NOT EXISTS financial_periods (
    period_id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    CONSTRAINT valid_period CHECK (end_date > start_date)
);

CREATE TABLE IF NOT EXISTS tax_rates (
    tax_id SERIAL PRIMARY KEY,
    tax_name VARCHAR(100) NOT NULL,
    rate DECIMAL(5, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS currencies (
    currency_code VARCHAR(3) PRIMARY KEY,
    currency_name VARCHAR(50) NOT NULL,
    exchange_rate DECIMAL(10, 6) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Inventory Tables
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit_price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id VARCHAR(10) NOT NULL REFERENCES warehouses(warehouse_id),
    quantity INT NOT NULL DEFAULT 0,
    reorder_point INT NOT NULL DEFAULT 10,
    unit_cost DECIMAL(10, 2) NOT NULL,
    last_count_date DATE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_product_warehouse UNIQUE (product_id, warehouse_id)
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id VARCHAR(20) PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    total_amount DECIMAL(15, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id VARCHAR(10) NOT NULL REFERENCES warehouses(warehouse_id),
    quantity INT NOT NULL,
    movement_type VARCHAR(20) NOT NULL,
    reference_id VARCHAR(20),
    movement_date TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_quantity CHECK (quantity != 0)
);

-- Sales Tables
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sales_orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    total_amount DECIMAL(15, 2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(15, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL REFERENCES sales_orders(order_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(15, 2) NOT NULL,
    CONSTRAINT valid_quantity CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL REFERENCES sales_orders(order_id),
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'unpaid',
    total_amount DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    invoice_id VARCHAR(20) NOT NULL REFERENCES invoices(invoice_id),
    payment_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    reference_number VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- HR Tables
CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS positions (
    position_id VARCHAR(10) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    department_id VARCHAR(10) NOT NULL REFERENCES departments(department_id),
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    department_id VARCHAR(10) NOT NULL REFERENCES departments(department_id),
    position_id VARCHAR(10) NOT NULL REFERENCES positions(position_id),
    salary DECIMAL(10, 2) NOT NULL,
    hire_date DATE NOT NULL,
    termination_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Update department manager foreign key
ALTER TABLE departments
ADD CONSTRAINT fk_manager_id FOREIGN KEY (manager_id) REFERENCES employees(employee_id);

CREATE TABLE IF NOT EXISTS payroll (
    payroll_id VARCHAR(20) PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    basic_salary DECIMAL(10, 2) NOT NULL,
    allowances DECIMAL(10, 2) NOT NULL DEFAULT 0,
    deductions DECIMAL(10, 2) NOT NULL DEFAULT 0,
    net_pay DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_period CHECK (pay_period_end > pay_period_start)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT unique_employee_date UNIQUE (employee_id, date)
);

-- Create ERP-specific functions
CREATE OR REPLACE FUNCTION calculate_inventory_value(warehouse_id_param VARCHAR DEFAULT NULL)
RETURNS TABLE (
    warehouse_id VARCHAR,
    warehouse_name VARCHAR,
    total_value DECIMAL(15, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.warehouse_id,
        w.name,
        COALESCE(SUM(i.quantity * i.unit_cost), 0) AS total_value
    FROM 
        warehouses w
    LEFT JOIN 
        inventory i ON w.warehouse_id = i.warehouse_id
    WHERE 
        (warehouse_id_param IS NULL OR w.warehouse_id = warehouse_id_param)
    GROUP BY 
        w.warehouse_id, w.name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_order_total(order_id_param VARCHAR)
RETURNS DECIMAL(15, 2) AS $$
DECLARE
    total DECIMAL(15, 2);
BEGIN
    SELECT SUM(line_total) INTO total
    FROM order_items
    WHERE order_id = order_id_param;
    
    RETURN COALESCE(total, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_account_balance(account_id_param VARCHAR)
RETURNS DECIMAL(15, 2) AS $$
DECLARE
    bal DECIMAL(15, 2);
BEGIN
    SELECT balance INTO bal
    FROM accounts
    WHERE account_id = account_id_param;
    
    RETURN COALESCE(bal, 0);
END;
$$ LANGUAGE plpgsql;

-- Insert sample data
INSERT INTO warehouses (warehouse_id, name, location)
VALUES 
    ('WH001', 'Main Warehouse', 'New York'),
    ('WH002', 'West Coast Warehouse', 'Los Angeles');

INSERT INTO products (product_id, name, description, unit_price, category)
VALUES 
    ('ITM001', 'Laptop', 'Business laptop with 16GB RAM', 1200.00, 'Electronics'),
    ('ITM002', 'Mouse', 'Wireless mouse', 25.00, 'Accessories');

INSERT INTO inventory (product_id, warehouse_id, quantity, reorder_point, unit_cost)
VALUES 
    ('ITM001', 'WH001', 15, 10, 1000.00),
    ('ITM002', 'WH001', 5, 20, 20.00),
    ('ITM001', 'WH002', 8, 10, 1000.00),
    ('ITM002', 'WH002', 25, 20, 20.00);

INSERT INTO departments (department_id, name)
VALUES 
    ('DEPT001', 'IT'),
    ('DEPT002', 'Sales'),
    ('DEPT003', 'Finance');

INSERT INTO positions (position_id, title, department_id, salary_min, salary_max)
VALUES 
    ('POS001', 'Developer', 'DEPT001', 70000.00, 120000.00),
    ('POS002', 'Sales Representative', 'DEPT002', 50000.00, 90000.00),
    ('POS003', 'Accountant', 'DEPT003', 60000.00, 100000.00);

INSERT INTO employees (employee_id, name, email, department_id, position_id, salary, hire_date)
VALUES 
    ('EMP001', 'John Doe', 'john.doe@example.com', 'DEPT001', 'POS001', 85000.00, '2022-01-15'),
    ('EMP002', 'Jane Smith', 'jane.smith@example.com', 'DEPT002', 'POS002', 65000.00, '2022-02-20'),
    ('EMP003', 'Bob Johnson', 'bob.johnson@example.com', 'DEPT003', 'POS003', 75000.00, '2022-03-10');

UPDATE departments SET manager_id = 'EMP001' WHERE department_id = 'DEPT001';
UPDATE departments SET manager_id = 'EMP002' WHERE department_id = 'DEPT002';
UPDATE departments SET manager_id = 'EMP003' WHERE department_id = 'DEPT003';

INSERT INTO customers (customer_id, name, email, phone, address)
VALUES 
    ('CUST001', 'Acme Corp', 'contact@acmecorp.com', '555-123-4567', '123 Business St, Commerce City'),
    ('CUST002', 'TechStart Inc', 'info@techstart.com', '555-987-6543', '456 Innovation Ave, Tech Park');

INSERT INTO accounts (account_id, account_name, account_type, balance)
VALUES 
    ('ACC001', 'Operating Account', 'Checking', 25000.00),
    ('ACC002', 'Payroll Account', 'Checking', 50000.00),
    ('ACC003', 'Tax Reserve', 'Savings', 15000.00); 