import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from .env file
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                    
                # Parse key-value pair
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value and (
                        (value.startswith("'") and value.endswith("'")) or 
                        (value.startswith('"') and value.endswith('"'))
                    ):
                        value = value[1:-1]
                        
                    # Set environment variable
                    os.environ[key] = value
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"Warning: .env file not found at {env_path}")
    except Exception as e:
        print(f"Error loading .env file: {e}")
        
    return env_vars

def check_required_vars(required_vars: list) -> bool:
    """
    Check if all required environment variables are set
    
    Args:
        required_vars: List of required environment variables
        
    Returns:
        True if all required variables are set, False otherwise
    """
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
            
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
        
    return True

def get_env(key: str, default: Any = None) -> Optional[str]:
    """
    Get environment variable with default fallback
    
    Args:
        key: Environment variable key
        default: Default value if key is not found
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)

if __name__ == "__main__":
    # Example usage
    env_file_path = sys.argv[1] if len(sys.argv) > 1 else ".env"
    loaded_vars = load_env_file(env_file_path)
    
    print(f"Loaded {len(loaded_vars)} environment variables from {env_file_path}")
    
    # Check required variables for ERP system
    required_vars = ["OPENAI_API_KEY", "ERP_DB_CONNECTION"]
    if check_required_vars(required_vars):
        print("All required environment variables are set")
    else:
        print("Please set the missing environment variables and try again") 