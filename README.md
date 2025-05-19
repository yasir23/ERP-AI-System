# ERP Agent System

An Intelligent ERP System built with the OpenAI Agents SDK.

## Overview

This system demonstrates how to build an enterprise-ready ERP application using the OpenAI Agents SDK. The application uses specialized agents for different ERP modules, along with a coordinator agent that delegates tasks appropriately. It features both a command-line interface and a web-based chat interface for interacting with the agents.

## Features

- **Specialized Agents**: Dedicated agents for Finance, Inventory, Sales, and HR
- **Coordinator Pattern**: Main agent that directs requests to appropriate specialized agents
- **Function Tools**: Domain-specific tools for each ERP module
- **Guardrails**: Security and domain-specific validation
- **MCP Integration**: Model Context Protocol servers for database and API connections
- **PostgreSQL Integration**: Full database schema and MCP database server connection
- **Chat Interface**: Web-based chat interface built with FastAPI and WebSockets

## Components

- **models.py**: Data models for the ERP system
- **tools.py**: Function tools for different ERP modules
- **guardrails.py**: Security and validation guardrails
- **agents.py**: Agent definitions and creation functions
- **mcp_integration.py**: Integration with MCP servers
- **erp_system.py**: Command-line application entry point
- **chat_frontend.py**: Web-based chat interface
- **db_schema.sql**: PostgreSQL database schema for the ERP system

## Architecture

The system is built around a layered architecture:

1. **Presentation Layer**: Chat interface with WebSockets for real-time communication
2. **Coordinator Layer**: Main agent that understands user requests and delegates
3. **Specialists Layer**: Domain-specific agents with specialized knowledge
4. **Tools Layer**: Python functions that interact with data
5. **MCP Layer**: PostgreSQL and API connections through MCP servers

## Setup

### Prerequisites

- Python 3.7+
- OpenAI API key
- Node.js (for MCP servers)
- PostgreSQL 12+ (for database integration)

### Database Setup

1. Install PostgreSQL and create a database:

```bash
createdb erp
```

2. Load the schema and sample data:

```bash
psql -d erp -f db_schema.sql
```

### Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
export OPENAI_API_KEY=sk-...
export ERP_DB_CONNECTION=postgresql://user:pass@localhost:5432/erp
export ERP_API_TOKEN=your_api_token
```

### Running the Application

#### Command Line Interface

```bash
python erp_system.py
```

#### Web Chat Interface

```bash
python chat_frontend.py
```

Then open your browser to http://localhost:8000 to use the chat interface.

## Usage Examples

### Finance Operations

```
ERP Request: Generate a financial report for Q2 2023
```

### Inventory Management

```
ERP Request: Check inventory levels for laptops and create a purchase order if below reorder point
```

### Sales Processing

```
ERP Request: Create a new sales order for customer ACME Corp for 5 laptops
```

### HR Management

```
ERP Request: Process payroll for the IT department
```

## PostgreSQL MCP Integration

The system uses the Model Context Protocol (MCP) to connect to the PostgreSQL database. This provides several advantages:

1. **Security**: The MCP server handles database connections and can control access permissions
2. **Standardization**: The MCP protocol provides a consistent interface for different data sources
3. **Flexibility**: The same agents can work with different database systems by changing the MCP configuration

### MCP Database Configuration

The MCP database server configuration includes:

- **Table Access**: Controls which tables the agents can access
- **Schema Control**: Limits access to specific database schemas
- **Function Access**: Allows the use of specific database functions
- **Write Permissions**: Controls whether agents can modify data

## Extending the System

### Adding New Tools

1. Define the tool function in tools.py
2. Add the tool to the appropriate agent in agents.py

### Adding New Guardrails

1. Create a new guardrail class in guardrails.py
2. Add the guardrail to the appropriate agent

### Adding MCP Servers

1. Create a setup function in mcp_integration.py
2. Call the function from erp_system.py or chat_frontend.py

### Extending the Database Schema

1. Add new tables or modify existing ones in db_schema.sql
2. Update the MCP configuration in mcp_integration.py

## License

MIT

## Acknowledgements

- OpenAI Agents SDK
- Model Context Protocol
- FastAPI
- PostgreSQL 