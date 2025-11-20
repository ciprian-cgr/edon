# EDON - Em Dash Object Notation

A cursed, token-minimal JSON flattening format designed to reduce LLM context usage.

## What is EDON?

EDON (Em Dash Object Notation) is a text format that flattens nested JSON structures into a hierarchical CSV-like format using dashes for indentation. The format is designed to be more token-efficient than JSON for large language models while remaining human-readable and easy to parse.

## Format Specification

### Structure

EDON uses a hierarchical format with dash-based indentation:

- Container names appear on their own lines
- Leaf properties are output as dash-separated keys followed by dash-separated values
- Each level of nesting adds one dash of indentation
- Arrays of objects include an index column (`#`) for tracking items

### Example

JSON:
```json
{
  "user": {
    "name": "Alice",
    "age": 30
  },
  "posts": [
    {"id": 1, "title": "First"},
    {"id": 2, "title": "Second"}
  ]
}
```

EDON:
```
user
-name-age-Alice-30
posts
-#-id-title
-0-1-First
-1-2-Second
```

### Key Features

- Hierarchical structure with dash indentation
- CSV-like rows for arrays (keys once, then values per item)
- Index column for array items
- No quotes needed for keys
- 4-7% token savings compared to JSON
- Preserves insertion order from source JSON

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
        "age": 30
    },
    "posts": [
        {"id": 1, "title": "First"},
        {"id": 2, "title": "Second"}
    ]
}

edon_text = edon.encode(obj)
print(edon_text)
# Output:
# user
# -name-age-Alice-30
# posts
# -#-id-title
# -0-1-First
# -1-2-Second

# Decode EDON to flat dictionary (reconstruction not supported)
decoded = edon.decode(edon_text)
# Returns a flat key-value mapping
```

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

#### Compare Token Counts

```bash
edon tokens input.json
```

Output:

```text
JSON chars:  1533
JSON tokens: 423

EDON chars:  1291
EDON tokens: 406

Saving: 17 tokens (4.0%)
```

### Demo Script

Run the demo to see EDON in action with the included test data:

```bash
python -m edon.demo
```

## Why EDON?

### Token Efficiency

EDON reduces token usage compared to JSON through:

1. **No structural overhead**: No braces, brackets, or quotes for keys
2. **Minimal punctuation**: Dashes for separation and indentation
3. **CSV-like arrays**: Keys listed once, values repeated in rows
4. **Compact format**: 4-7% token savings on typical nested data

### When to Use EDON

- Passing large JSON datasets to LLMs with token limits
- Storing data in LLM context windows more efficiently
- Debugging nested structures in a flat, readable format
- Cases where you need human-readable tabular format

### When NOT to Use EDON

- When full JSON round-trip reconstruction is required
- For very small objects (overhead may exceed savings)
- When you need streaming or partial parsing
- When JSON compatibility is strictly required

## API Reference

### `encode(obj: Any) -> str`

Serialize a JSON-compatible Python object to EDON text.

**Parameters:**

- `obj`: Any JSON-compatible Python object

**Returns:**

- EDON text as a string

### `decode(text: str) -> dict`

Parse EDON text into a flat key-value mapping.

Note: Full reconstruction to original nested structure is not supported.

**Parameters:**

- `text`: EDON text as a string

**Returns:**

- Flat dictionary mapping paths to values

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

EDON is inspired by the need for more efficient data formats for LLM context usage. The format prioritizes simplicity and token efficiency over features like streaming or schema validation.
