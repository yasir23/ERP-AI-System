from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import json
import os
import uvicorn
import asyncio
from datetime import datetime
from pathlib import Path

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

# Initialize FastAPI app
app = FastAPI(title="Simple ERP Chat Interface")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory message storage for chat history
chat_histories = {}

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

# Create ERP agent
def create_erp_agent():
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
    
    return agent

# Initialize agent on startup
@app.on_event("startup")
async def startup_event():
    # Load environment variables
    load_env_file()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY"]
    if not check_required_vars(required_vars):
        raise Exception("Missing required environment variables")
    
    # Initialize agent and runner
    app.state.agent = create_erp_agent()
    app.state.runner = Runner()

# WebSocket endpoint for chat
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    # Initialize chat history for this user if it doesn't exist
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    try:
        while True:
            # Receive message from websocket
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Store user message in history
            timestamp = datetime.now().isoformat()
            user_message = {
                "role": "user",
                "content": message_data["message"],
                "timestamp": timestamp
            }
            chat_histories[user_id].append(user_message)
            
            # Process message with ERP agent
            try:
                # Send "thinking" message to indicate processing
                await manager.send_message(
                    json.dumps({"status": "thinking", "timestamp": timestamp}),
                    user_id
                )
                
                # Process with agent
                result = await app.state.runner.run(
                    app.state.agent, 
                    message_data["message"]
                )
                
                # Store and send agent response
                assistant_message = {
                    "role": "assistant",
                    "content": result.final_output,
                    "timestamp": datetime.now().isoformat()
                }
                chat_histories[user_id].append(assistant_message)
                
                await manager.send_message(
                    json.dumps(assistant_message),
                    user_id
                )
            except Exception as e:
                # Handle errors in agent processing
                error_message = {
                    "role": "system",
                    "content": f"Error processing request: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                chat_histories[user_id].append(error_message)
                await manager.send_message(json.dumps(error_message), user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# REST API endpoints for chat history
@app.get("/chat_history/{user_id}")
async def get_chat_history(user_id: str):
    if user_id not in chat_histories:
        return {"messages": []}
    return {"messages": chat_histories[user_id]}

# Serve static files (HTML/CSS/JS for chat interface)
@app.get("/")
async def get_index():
    return {"message": "Simple ERP Chat API is running. Web interface available at /chat"}

# Function to ensure the static directory exists
def ensure_static_dir():
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    chat_html = static_dir / "index.html"
    
    # Create the HTML file if it doesn't exist
    if not chat_html.exists():
        with open(chat_html, "w") as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple ERP Chat Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #1a73e8;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            width: 100%;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .message {
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #e3f2fd;
            align-self: flex-end;
            border-bottom-right-radius: 0.3rem;
        }
        .assistant-message {
            background-color: #f1f1f1;
            align-self: flex-start;
            border-bottom-left-radius: 0.3rem;
        }
        .system-message {
            background-color: #ffebee;
            align-self: center;
            font-style: italic;
            font-size: 0.9rem;
        }
        .thinking {
            background-color: #f1f1f1;
            align-self: flex-start;
            opacity: 0.6;
            font-style: italic;
        }
        .timestamp {
            font-size: 0.7rem;
            opacity: 0.6;
            margin-top: 0.3rem;
        }
        .input-area {
            display: flex;
            padding: 1rem;
            gap: 0.5rem;
            background-color: white;
            border-top: 1px solid #e0e0e0;
        }
        #message-input {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
            border-radius: 1.5rem;
            outline: none;
        }
        #send-button {
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 1.5rem;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
        }
        #send-button:hover {
            background-color: #1557b0;
        }
        .helper-text {
            text-align: center;
            margin: 1rem;
            color: #666;
            font-size: 0.9rem;
        }
        .examples {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin: 0.5rem 0 1rem;
        }
        .example-chip {
            background-color: #e3f2fd;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            cursor: pointer;
            font-size: 0.9rem;
        }
        .example-chip:hover {
            background-color: #bbdefb;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Simple ERP Chat Assistant</h1>
    </div>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message assistant-message">
                Hello! I'm your ERP assistant. How can I help you today?
            </div>
        </div>
        <div class="helper-text">
            Here are some example queries you can try:
        </div>
        <div class="examples">
            <div class="example-chip" onclick="useExample(this)">Check inventory for laptops</div>
            <div class="example-chip" onclick="useExample(this)">Get employee data for EMP001</div>
            <div class="example-chip" onclick="useExample(this)">Get customer info for CUST001</div>
            <div class="example-chip" onclick="useExample(this)">Process payroll for IT department</div>
        </div>
        <div class="input-area">
            <input type="text" id="message-input" placeholder="Type your request...">
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        // Generate a random user ID for this session
        const userId = 'user_' + Math.random().toString(36).substring(2, 10);
        let socket;

        function connectWebSocket() {
            // Connect to WebSocket
            socket = new WebSocket(`ws://${window.location.host}/ws/${userId}`);
            
            socket.onopen = function(e) {
                console.log("WebSocket connection established");
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                // Handle "thinking" status
                if (data.status === "thinking") {
                    const thinkingDiv = document.createElement('div');
                    thinkingDiv.className = 'message thinking';
                    thinkingDiv.id = 'thinking-indicator';
                    thinkingDiv.textContent = 'Thinking...';
                    document.getElementById('messages').appendChild(thinkingDiv);
                    scrollToBottom();
                    return;
                }
                
                // Remove thinking indicator if exists
                const thinkingIndicator = document.getElementById('thinking-indicator');
                if (thinkingIndicator) {
                    thinkingIndicator.remove();
                }
                
                // Create message element
                const messageDiv = document.createElement('div');
                
                // Set class based on role
                if (data.role === 'user') {
                    messageDiv.className = 'message user-message';
                } else if (data.role === 'assistant') {
                    messageDiv.className = 'message assistant-message';
                } else {
                    messageDiv.className = 'message system-message';
                }
                
                // Set content
                messageDiv.textContent = data.content;
                
                // Add timestamp
                const timestamp = document.createElement('div');
                timestamp.className = 'timestamp';
                const date = new Date(data.timestamp);
                timestamp.textContent = date.toLocaleTimeString();
                messageDiv.appendChild(timestamp);
                
                // Add to messages
                document.getElementById('messages').appendChild(messageDiv);
                
                // Scroll to bottom
                scrollToBottom();
            };

            socket.onclose = function(event) {
                console.log("WebSocket connection closed, reconnecting in 3 seconds...");
                setTimeout(connectWebSocket, 3000);
            };

            socket.onerror = function(error) {
                console.error("WebSocket error:", error);
            };
        }

        window.onload = function() {
            connectWebSocket();
            
            // Load chat history
            fetch(`/chat_history/${userId}`)
                .then(response => response.json())
                .then(data => {
                    // Display existing messages
                    data.messages.forEach(message => {
                        const messageDiv = document.createElement('div');
                        
                        if (message.role === 'user') {
                            messageDiv.className = 'message user-message';
                        } else if (message.role === 'assistant') {
                            messageDiv.className = 'message assistant-message';
                        } else {
                            messageDiv.className = 'message system-message';
                        }
                        
                        messageDiv.textContent = message.content;
                        
                        const timestamp = document.createElement('div');
                        timestamp.className = 'timestamp';
                        const date = new Date(message.timestamp);
                        timestamp.textContent = date.toLocaleTimeString();
                        messageDiv.appendChild(timestamp);
                        
                        document.getElementById('messages').appendChild(messageDiv);
                    });
                    
                    scrollToBottom();
                });
            
            // Send message on button click
            document.getElementById('send-button').addEventListener('click', sendMessage);
            
            // Send message on Enter key
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        };

        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (message === '') return;
            
            // Create message object
            const messageObj = {
                message: message
            };
            
            // Send message to server
            socket.send(JSON.stringify(messageObj));
            
            // Create user message element
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message';
            messageDiv.textContent = message;
            
            const timestamp = document.createElement('div');
            timestamp.className = 'timestamp';
            timestamp.textContent = new Date().toLocaleTimeString();
            messageDiv.appendChild(timestamp);
            
            document.getElementById('messages').appendChild(messageDiv);
            
            // Clear input
            input.value = '';
            
            // Scroll to bottom
            scrollToBottom();
        }

        function scrollToBottom() {
            const messages = document.getElementById('messages');
            messages.scrollTop = messages.scrollHeight;
        }
        
        function useExample(element) {
            const input = document.getElementById('message-input');
            input.value = element.textContent;
            input.focus();
        }
    </script>
</body>
</html>
            """)
    
    return static_dir

# Mount static files after creating them
@app.on_event("startup")
async def create_static_files():
    static_dir = ensure_static_dir()
    app.mount("/chat", StaticFiles(directory=static_dir, html=True), name="static")

# Run the app
if __name__ == "__main__":
    # Load environment variables 
    load_env_file()
    
    # Get host and port from environment or use defaults
    host = get_env("CHAT_INTERFACE_HOST", "0.0.0.0")
    port = int(get_env("CHAT_INTERFACE_PORT", "8000"))
    
    # Start the server
    uvicorn.run(app, host=host, port=port) 