"""
EDON codec - Em Dash Object Notation encoding and decoding.

This module provides functions to convert between JSON-compatible Python objects
and EDON text format, which flattens nested structures into path—value lines.
"""

import json
import re
from typing import Any, Iterable, Tuple, Dict, List, Union


def iter_pairs(obj: Any, prefix: str = "") -> Iterable[Tuple[str, str]]:
    """
    Flatten a JSON-compatible object into (path, json_literal_value) pairs.

    Args:
        obj: A JSON-compatible Python object (dict, list, or primitive).
        prefix: Internal parameter for tracking the current path.

    Yields:
        Tuples of (path, value_literal) where value_literal is a JSON string.

    Example:
        >>> list(iter_pairs({"a": 1, "b": [2, 3]}))
        [('a', '1'), ('b[0]', '2'), ('b[1]', '3')]
    """
    if isinstance(obj, dict):
        if not obj:
            # Empty dict - emit a marker
            path = prefix if prefix else "$"
            yield path, "{}"
        else:
            for key in sorted(obj.keys()):
                new_prefix = f"{prefix}.{key}" if prefix else key
                yield from iter_pairs(obj[key], new_prefix)
    elif isinstance(obj, list):
        if not obj:
            # Empty list - emit a marker
            path = prefix if prefix else "$"
            yield path, "[]"
        else:
            for i, item in enumerate(obj):
                new_prefix = f"{prefix}[{i}]"
                yield from iter_pairs(item, new_prefix)
    else:
        # Primitive value (string, number, boolean, null)
        path = prefix if prefix else "$"
        value_literal = json.dumps(obj, ensure_ascii=True, separators=(",", ":"))
        yield path, value_literal


def encode(obj: Any) -> str:
    """
    Serialize a JSON-compatible Python object to EDON text.

    The output is a series of lines in the format:
        path—value

    Where:
    - path uses dots for object keys and brackets for array indices
    - — is a single Unicode em dash (U+2014)
    - value is a JSON literal with ensure_ascii=True
    - Lines are sorted lexicographically by path

    Args:
        obj: A JSON-compatible Python object.

    Returns:
        EDON text as a string.

    Example:
        >>> encode({"user": {"name": "Alice", "age": 30}})
        'user.age—30\\nuser.name—"Alice"'
    """
    pairs = list(iter_pairs(obj))
    pairs.sort(key=lambda p: p[0])
    lines = [f"{path}—{value}" for path, value in pairs]
    return "\n".join(lines)


def _parse_path(path: str) -> List[Union[str, int]]:
    """
    Parse a path string into a list of components (keys and indices).

    Args:
        path: A path string like "user.items[0].name"

    Returns:
        List of components, where strings are object keys and ints are array indices.

    Example:
        >>> _parse_path("user.items[0].name")
        ['user', 'items', 0, 'name']
    """
    if path == "$":
        return []

    components = []
    # Split by dots and brackets
    # Pattern: match either a word or [number]
    pattern = r'([^.\[\]]+)|\[(\d+)\]'
    matches = re.findall(pattern, path)

    for key, idx in matches:
        if key:
            components.append(key)
        elif idx:
            components.append(int(idx))

    return components


def from_pairs(pairs: Iterable[Tuple[str, str]]) -> Any:
    """
    Reconstruct a JSON object from (path, json_literal_value) pairs.

    Args:
        pairs: Iterable of (path, value_literal) tuples.

    Returns:
        A reconstructed Python object (dict, list, or primitive).

    Example:
        >>> from_pairs([('a', '1'), ('b[0]', '2')])
        {'a': 1, 'b': [2]}
    """
    root = None
    root_is_primitive = False

    for path, value_literal in pairs:
        # Check if this is an empty collection marker
        if value_literal == "{}":
            value = {}
            is_empty_collection = True
        elif value_literal == "[]":
            value = []
            is_empty_collection = True
        else:
            value = json.loads(value_literal)
            is_empty_collection = False

        components = _parse_path(path)

        # Handle top-level value (primitive or empty collection)
        if not components:
            root = value
            root_is_primitive = True
            continue

        # Initialize root if needed
        if root is None:
            # Determine if root should be dict or list
            if isinstance(components[0], int):
                root = []
            else:
                root = {}

        # Navigate to the parent of the target location
        current = root
        for i, component in enumerate(components[:-1]):
            next_component = components[i + 1]

            if isinstance(component, str):
                # Current should be a dict
                if not isinstance(current, dict):
                    raise ValueError(f"Expected dict at {component}, got {type(current)}")

                if component not in current:
                    # Determine what to create based on next component
                    if isinstance(next_component, int):
                        current[component] = []
                    else:
                        current[component] = {}

                current = current[component]
            else:  # isinstance(component, int)
                # Current should be a list
                if not isinstance(current, list):
                    raise ValueError(f"Expected list at [{component}], got {type(current)}")

                # Extend list if necessary
                while len(current) <= component:
                    current.append(None)

                if current[component] is None:
                    # Determine what to create based on next component
                    if isinstance(next_component, int):
                        current[component] = []
                    else:
                        current[component] = {}

                current = current[component]

        # Set the final value
        final_component = components[-1]
        if isinstance(final_component, str):
            if not isinstance(current, dict):
                raise ValueError(f"Expected dict for key {final_component}, got {type(current)}")
            current[final_component] = value
        else:  # isinstance(final_component, int)
            if not isinstance(current, list):
                raise ValueError(f"Expected list for index [{final_component}], got {type(current)}")
            # Extend list if necessary
            while len(current) <= final_component:
                current.append(None)
            current[final_component] = value

    return root


def decode(text: str) -> Any:
    """
    Parse EDON text back into a nested Python structure.

    Each non-empty line must be in the format:
        path—value

    Where:
    - path is parsed into components (keys and indices)
    - — is a single Unicode em dash (U+2014)
    - value is a JSON literal

    Args:
        text: EDON text as a string.

    Returns:
        A reconstructed Python object (dict, list, or primitive).

    Example:
        >>> decode('user.age—30\\nuser.name—"Alice"')
        {'user': {'age': 30, 'name': 'Alice'}}
    """
    pairs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Split on the first em dash
        if "—" not in line:
            raise ValueError(f"Invalid EDON line (missing em dash): {line}")

        path, value_literal = line.split("—", 1)
        pairs.append((path, value_literal))

    return from_pairs(pairs)
