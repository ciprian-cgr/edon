"""
EDON codec - Em Dash Object Notation encoding and decoding.

This module provides functions to convert between JSON-compatible Python objects
and EDON text format, which uses em dashes as separators in a table-like structure.
"""

import json
from typing import Any, Dict, List, Tuple, Union


def encode(obj: Any) -> str:
    """
    Serialize a JSON-compatible Python object to EDON text.

    The output uses em dashes (—) as separators in a table-like format:
    - For nested containers: —<container_id>—<parent_id>—<key_or_index>
    - For primitive values: —<container_id>—<key_or_index>—<value>

    Args:
        obj: A JSON-compatible Python object.

    Returns:
        EDON text as a string.

    Example:
        >>> encode({"x": 1})
        '—0—x—1'
        >>> encode({"user": {"name": "Alice"}})
        '—1—0—user\\n—1—name—"Alice"'
    """
    # First pass: assign container IDs
    container_map = {}  # id(object) -> container_id
    next_id = [1]  # Start at 1, root is always 0

    def assign_ids(node: Any, parent_id: int, key: Union[str, int]) -> None:
        """Recursively assign container IDs to nested objects/arrays."""
        if isinstance(node, (dict, list)):
            if id(node) not in container_map:
                container_id = next_id[0]
                next_id[0] += 1
                container_map[id(node)] = container_id

                # Recurse into children
                if isinstance(node, dict):
                    for k, v in node.items():
                        assign_ids(v, container_id, k)
                else:  # list
                    for i, v in enumerate(node):
                        assign_ids(v, container_id, i)

    # Root container is always ID 0
    if isinstance(obj, (dict, list)):
        container_map[id(obj)] = 0
        if isinstance(obj, dict):
            for k, v in obj.items():
                assign_ids(v, 0, k)
        else:  # list
            for i, v in enumerate(obj):
                assign_ids(v, 0, i)

    # Second pass: generate EDON lines
    lines = []

    def generate_lines(node: Any, container_id: int) -> None:
        """Generate EDON lines for a container and its contents."""
        if isinstance(node, dict):
            for key in sorted(node.keys()):
                value = node[key]
                # JSON-encode dict keys to distinguish them from list indices
                key_str = json.dumps(key, ensure_ascii=True)
                if isinstance(value, (dict, list)) and len(value) > 0:
                    # Non-empty nested container declaration
                    child_id = container_map[id(value)]
                    lines.append(f"—{child_id}—{container_id}—{key_str}")
                    generate_lines(value, child_id)
                elif isinstance(value, (dict, list)) and len(value) == 0:
                    # Empty collection - treat as primitive value
                    value_str = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
                    lines.append(f"—{container_id}—{key_str}—{value_str}")
                else:
                    # Primitive value
                    value_str = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
                    lines.append(f"—{container_id}—{key_str}—{value_str}")
        elif isinstance(node, list):
            for idx, value in enumerate(node):
                if isinstance(value, (dict, list)) and len(value) > 0:
                    # Non-empty nested container declaration
                    child_id = container_map[id(value)]
                    lines.append(f"—{child_id}—{container_id}—{idx}")
                    generate_lines(value, child_id)
                elif isinstance(value, (dict, list)) and len(value) == 0:
                    # Empty collection - treat as primitive value
                    value_str = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
                    lines.append(f"—{container_id}—{idx}—{value_str}")
                else:
                    # Primitive value
                    value_str = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
                    lines.append(f"—{container_id}—{idx}—{value_str}")
        else:
            # Top-level primitive
            value_str = json.dumps(node, ensure_ascii=True, separators=(",", ":"))
            lines.append(f"—0—$—{value_str}")

    if isinstance(obj, (dict, list)):
        generate_lines(obj, 0)
    else:
        # Top-level primitive
        value_str = json.dumps(obj, ensure_ascii=True, separators=(",", ":"))
        lines.append(f"—0—$—{value_str}")

    return "\n".join(lines)


def decode(text: str) -> Any:
    """
    Parse EDON text back into a nested Python structure.

    Each non-empty line must be in the format:
        —<container_id>—<key_or_parent>—<value_or_key>

    Args:
        text: EDON text as a string.

    Returns:
        A reconstructed Python object (dict, list, or primitive).

    Example:
        >>> decode('—0—x—1')
        {'x': 1}
        >>> decode('—1—0—user\\n—1—name—"Alice"')
        {'user': {'name': 'Alice'}}
    """
    if not text.strip():
        return None

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Container structure: {container_id: {'type': 'dict'|'list', 'parent': id, 'key': key, 'data': {}}}
    containers = {}
    seen_containers = set()  # Track which container IDs we've seen

    # First pass: identify all lines and categorize them
    parsed_lines = []
    for line in lines:
        parts = line.split("—")
        if len(parts) < 4:
            raise ValueError(f"Invalid EDON line: {line}")

        # Remove empty first element (line starts with —)
        parts = parts[1:]

        if len(parts) != 3:
            raise ValueError(f"Invalid EDON line: {line}")

        try:
            container_id = int(parts[0])
        except ValueError:
            raise ValueError(f"Invalid EDON line (container_id must be integer): {line}")

        second_field = parts[1]
        third_field = parts[2]

        # A line is a container declaration if:
        # 1. This container_id hasn't been seen before, AND
        # 2. The container_id is NOT 0 (root is never declared), AND
        # 3. The second field is numeric (parent ID)
        is_declaration = False
        if container_id != 0 and container_id not in seen_containers:
            try:
                parent_id = int(second_field)
                is_declaration = True
                seen_containers.add(container_id)

                # Create container entry
                containers[container_id] = {
                    'type': None,
                    'parent': parent_id,
                    'key': third_field,
                    'data': None
                }
            except ValueError:
                pass

        if not is_declaration:
            # It's a value line
            parsed_lines.append(('value', container_id, second_field, third_field))

    # Initialize root container
    if 0 not in containers:
        containers[0] = {'type': None, 'parent': None, 'key': None, 'data': None}

    # Second pass: process value lines to determine container types and populate data
    for line_type, container_id, key_or_index, value_str in parsed_lines:
        # Ensure container exists
        if container_id not in containers:
            containers[container_id] = {'type': None, 'parent': None, 'key': None, 'data': None}

        # Special case: top-level primitive
        if key_or_index == "$":
            value = json.loads(value_str)
            return value

        # Determine container type based on key/index
        # If it's a JSON string (starts with "), it's a dict key
        if key_or_index.startswith('"'):
            # It's a dict
            if containers[container_id]['type'] is None:
                containers[container_id]['type'] = 'dict'
                containers[container_id]['data'] = {}
        else:
            # Try to parse as integer - if successful, it's a list index
            try:
                index = int(key_or_index)
                # It's numeric, so this is a list
                if containers[container_id]['type'] is None:
                    containers[container_id]['type'] = 'list'
                    containers[container_id]['data'] = []
            except ValueError:
                # It's a non-quoted, non-numeric string - treat as dict key
                if containers[container_id]['type'] is None:
                    containers[container_id]['type'] = 'dict'
                    containers[container_id]['data'] = {}

    # Third pass: populate values
    for line_type, container_id, key_or_index, value_str in parsed_lines:
        value = json.loads(value_str)
        container = containers[container_id]

        if container['type'] == 'dict':
            # JSON-decode the key if it's encoded
            if key_or_index.startswith('"'):
                key = json.loads(key_or_index)
            else:
                key = key_or_index
            container['data'][key] = value
        elif container['type'] == 'list':
            index = int(key_or_index)
            # Extend list if needed
            while len(container['data']) <= index:
                container['data'].append(None)
            container['data'][index] = value

    # Fourth pass: build hierarchy by inserting containers into their parents
    for container_id in sorted(containers.keys(), reverse=True):  # Process bottom-up
        if container_id == 0:
            continue

        info = containers[container_id]
        if info['parent'] is None:
            continue

        parent = containers[info['parent']]
        key_or_index = info['key']

        # Determine parent type if not set based on the key format
        if parent['type'] is None:
            if key_or_index.startswith('"'):
                parent['type'] = 'dict'
                parent['data'] = {}
            else:
                try:
                    int(key_or_index)
                    parent['type'] = 'list'
                    parent['data'] = []
                except ValueError:
                    parent['type'] = 'dict'
                    parent['data'] = {}

        # Insert child into parent
        child_data = containers[container_id]['data']
        if parent['type'] == 'dict':
            # JSON-decode the key if it's encoded
            if key_or_index.startswith('"'):
                key = json.loads(key_or_index)
            else:
                key = key_or_index
            parent['data'][key] = child_data
        elif parent['type'] == 'list':
            index = int(key_or_index)
            while len(parent['data']) <= index:
                parent['data'].append(None)
            parent['data'][index] = child_data

    return containers[0]['data']


# Maintain backward compatibility
def iter_pairs(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """
    Legacy function for backward compatibility.
    Note: The new EDON format doesn't use path-based pairs anymore.
    """
    raise NotImplementedError("iter_pairs is not supported in the new EDON format")


def from_pairs(pairs: List[Tuple[str, str]]) -> Any:
    """
    Legacy function for backward compatibility.
    Note: The new EDON format doesn't use path-based pairs anymore.
    """
    raise NotImplementedError("from_pairs is not supported in the new EDON format")
