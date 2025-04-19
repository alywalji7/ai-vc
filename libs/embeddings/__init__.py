"""
Text, code, and table embedding utilities using Hugging Face models.
"""

from libs.embeddings.embeddings import (
    get_model,
    embed_text,
    embed_code,
    embed_table,
)

__all__ = [
    "get_model",
    "embed_text",
    "embed_code",
    "embed_table",
]