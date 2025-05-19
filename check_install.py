import importlib
import sys
import os

def check_module(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown version")
        print(f"✅ {module_name}: Installed ({version})")
        return True
    except ImportError:
        print(f"❌ {module_name}: Not installed")
        return False

def check_environment():
    print("\n=== Environment Variables ===")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        # Mask API key for security
        masked_key = api_key[:4] + "..." + api_key[-4:]
        print(f"✅ OPENAI_API_KEY: Set ({masked_key})")
    else:
        print("❌ OPENAI_API_KEY: Not set")

if __name__ == "__main__":
    print("=== Checking Required Dependencies ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required modules
    REQUIRED_MODULES = ["agents", "openai", "fastapi", "uvicorn", "websockets", "pydantic"]
    
    all_installed = True
    for module in REQUIRED_MODULES:
        if not check_module(module):
            all_installed = False
    
    # Check environment variables
    check_environment()
    
    # Print summary
    print("\n=== Summary ===")
    if all_installed:
        print("All required dependencies are installed! 🎉")
    else:
        print("Some dependencies are missing. Please install them with:")
        print("pip install -r requirements.txt")
    
    print("\n=== Run Instructions ===")
    print("1. Command-line interface: python demo_simple.py")
    print("2. Web interface: python demo_web.py and visit http://localhost:8000/chat") 