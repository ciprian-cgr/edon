"""
EDON - Em Dash Object Notation

A cursed, token-minimal JSON flattening format.

Example:
    >>> import edon
    >>> obj = {"user": {"name": "Alice", "age": 30}}
    >>> text = edon.encode(obj)
    >>> print(text)
    user.age—30
    user.name—"Alice"
    >>> edon.decode(text) == obj
    True
"""

from .codec import encode, decode, iter_pairs, from_pairs

__version__ = "0.1.0"
__all__ = ["encode", "decode", "iter_pairs", "from_pairs"]
