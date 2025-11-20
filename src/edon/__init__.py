"""
EDON - Em Dash Object Notation

A token-minimal JSON flattening format for LLM context efficiency.

Example:
    >>> import edon
    >>> obj = {"user": {"name": "Alice", "age": 30}}
    >>> text = edon.encode(obj)
    >>> print(text)
    user
    -name-age-Alice-30

Note: decode() is not supported for reconstruction to nested JSON.
"""

from .codec.codec import decode, encode

__version__ = "0.1.0"
__all__ = ["encode", "decode"]
