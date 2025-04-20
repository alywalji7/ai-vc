"""
Utility functions for models in the Term Sheet Generator & Negotiator Bot.
"""

from datetime import datetime


def pydantic_to_dict(obj):
    """
    Convert a Pydantic model to a dictionary correctly handling nested models.
    
    Args:
        obj: Pydantic model instance
        
    Returns:
        Dictionary representation of the model
    """
    if hasattr(obj, 'dict'):
        return obj.dict()
    return obj