"""
Text, code, and table embedding utilities using Hugging Face models.
"""

from libs.embeddings.embeddings import (
    embed_text,
    embed_code,
    embed_table,
    get_model,
)

__all__ = ["embed_text", "embed_code", "embed_table", "get_model"]