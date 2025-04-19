import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Union

# Set up logging
logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    """Extended JSON encoder to handle dates and datetimes."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def serialize_to_json(data: Union[Dict, List]) -> str:
    """
    Serialize a dictionary or list to a JSON string.
    
    Args:
        data: The data to serialize
        
    Returns:
        A JSON string representation of the data
    """
    return json.dumps(data, cls=JSONEncoder)

def deserialize_from_json(json_str: str) -> Union[Dict, List]:
    """
    Deserialize a JSON string to a Python object.
    
    Args:
        json_str: The JSON string to deserialize
        
    Returns:
        The deserialized Python object
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Error deserializing JSON: {e}")
        raise

def format_error_response(message: str, code: int = 400) -> Dict[str, Any]:
    """
    Format a standardized error response.
    
    Args:
        message: The error message
        code: The HTTP status code
        
    Returns:
        A dictionary with error details
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

def is_valid_email(email: str) -> bool:
    """
    Validate if a string is a proper email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def truncate_string(string: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length and add ellipsis if truncated.
    
    Args:
        string: The string to truncate
        max_length: The maximum length
        
    Returns:
        The truncated string
    """
    if len(string) <= max_length:
        return string
    return string[:max_length - 3] + '...'
