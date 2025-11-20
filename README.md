# EDON - Em Dash Object Notation

A cursed, token-minimal JSON flattening format designed to reduce LLM context usage.

## What is EDON?

EDON (Em Dash Object Notation) is a text format that flattens nested JSON structures into a series of simple `path—value` lines, where the path and value are separated by an em dash (—). The format is designed to be more token-efficient than JSON for large language models while remaining human-readable and easy to parse.

## Format Specification

### Line Format

Each line in EDON represents a single primitive value:

```
<path>—<value>
```

- `path`: A dot-separated path for object keys, with `[index]` notation for arrays
- `—`: A single Unicode em dash (U+2014) separator
- `value`: A JSON literal value (string, number, boolean, or null)

### Example

JSON:
```json
{
  "user": {
    "name": "Alice",
    "age": 30,
    "roles": ["admin", "user"]
  }
}
```

EDON:
```
user.age—30
user.name—"Alice"
user.roles[0]—"admin"
user.roles[1]—"user"
```

### Key Features

- Lines are sorted lexicographically by path for determinism
- String values use `ensure_ascii=True` to prevent em dashes in values from conflicting with the separator
- Works with any JSON-compatible data structure (objects, arrays, primitives)
- Top-level primitives use the path `$`

## Installation

```bash
pip install edon
```

## Usage

### Python API

```python
import edon

# Encode Python object to EDON
obj = {
    "user": {
        "name": "Alice",
        "age": 30,
        "roles": ["admin", "user"]
    }
}

edon_text = edon.encode(obj)
print(edon_text)
# Output:
# user.age—30
# user.name—"Alice"
# user.roles[0]—"admin"
# user.roles[1]—"user"

# Decode EDON back to Python object
decoded = edon.decode(edon_text)
assert decoded == obj  # Round-trip successful!
```

### Command-Line Interface

#### Encode JSON to EDON

```bash
edon encode input.json > output.edon
cat input.json | edon encode - > output.edon
```

#### Decode EDON to JSON

```bash
edon decode input.edon > output.json
cat input.edon | edon decode - > output.json
```

#### Compare Token Counts

```bash
edon tokens input.json
```

Output:
```
JSON chars:  1234
JSON tokens: 250

EDON chars:  980
EDON tokens: 210

Saving: 40 tokens (16.0%)
```

### Demo Script

Run the demo to see EDON in action with the included test data:

```bash
python -m edon.demo
```

## Why EDON?

### Token Efficiency

EDON can reduce token usage compared to JSON, especially for nested structures:

1. **No structural overhead**: No braces, brackets, or quotes for keys
2. **Minimal punctuation**: Single em dash separator per value
3. **Sorted output**: Consistent ordering for better compression

### When to Use EDON

- Passing large JSON datasets to LLMs with token limits
- Storing data in LLM context windows more efficiently
- Debugging nested structures in a flat, readable format
- Cases where you need deterministic serialization

### When NOT to Use EDON

- When JSON compatibility is required
- When the overhead of flattening/unflattening is significant
- For very small objects (overhead of paths may exceed savings)
- When you need streaming or partial parsing

## Format Details

### Path Syntax

- Object keys: `parent.child`
- Array indices: `parent[0]`
- Nested: `order.items[0].price`
- Top-level primitive: `$`

### Value Encoding

Values are JSON literals with `ensure_ascii=True`:

- Strings: `"Alice"` (with escape sequences)
- Numbers: `30` or `3.14`
- Booleans: `true` or `false`
- Null: `null`

### Em Dash Safety

The em dash (—) is used as the separator because:

1. It's rare in typical data
2. It's a single Unicode character
3. When it does appear in strings, it's automatically escaped by JSON as `\u2014`

This ensures unambiguous parsing: split each line on the first em dash.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ciprian-cgr/edon.git
cd edon

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Demo

```bash
python -m edon.demo
```

### Format Code

```bash
black src tests
ruff check src tests
```

### Type Checking

```bash
mypy src
```

## API Reference

### `encode(obj: Any) -> str`

Serialize a JSON-compatible Python object to EDON text.

**Parameters:**
- `obj`: Any JSON-compatible Python object

**Returns:**
- EDON text as a string

### `decode(text: str) -> Any`

Parse EDON text back into a nested Python structure.

**Parameters:**
- `text`: EDON text as a string

**Returns:**
- Reconstructed Python object

### `iter_pairs(obj: Any) -> Iterable[Tuple[str, str]]`

Flatten an object into (path, json_literal_value) pairs.

**Parameters:**
- `obj`: Any JSON-compatible Python object

**Yields:**
- Tuples of `(path, value_literal)`

### `from_pairs(pairs: Iterable[Tuple[str, str]]) -> Any`

Reconstruct a JSON object from (path, json_literal_value) pairs.

**Parameters:**
- `pairs`: Iterable of `(path, value_literal)` tuples

**Returns:**
- Reconstructed Python object

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

EDON is inspired by the need for more efficient data formats for LLM context usage. The format prioritizes simplicity and token efficiency over features like streaming or schema validation.
