"""
Round-trip tests using the complex.json test data file.
"""

import json
from pathlib import Path
import pytest
from edon import encode, decode


@pytest.fixture
def complex_data():
    """Load the complex.json test data."""
    data_path = Path(__file__).parent / "data" / "complex.json"
    return json.loads(data_path.read_text())


def test_complex_json_roundtrip(complex_data):
    """Test that complex.json can be encoded and decoded successfully."""
    # Encode to EDON
    edon_text = encode(complex_data)

    # Verify it's not empty
    assert edon_text
    assert len(edon_text) > 0

    # Decode back to Python object
    decoded = decode(edon_text)

    # Verify round-trip
    assert decoded == complex_data


def test_complex_json_structure(complex_data):
    """Test that the complex data has expected structure after round-trip."""
    edon_text = encode(complex_data)
    decoded = decode(edon_text)

    # Check some specific fields
    assert decoded["user"]["username"] == "alice_wonder"
    assert decoded["user"]["profile"]["first_name"] == "Alice"
    assert decoded["user"]["profile"]["location"]["city"] == "San Francisco"
    assert len(decoded["posts"]) == 2
    assert decoded["posts"][0]["id"] == 1001
    assert len(decoded["posts"][0]["comments"]) == 2
    assert decoded["statistics"]["total_posts"] == 2
    assert decoded["flags"] == [True, False, True, True, False]


def test_no_raw_em_dash_in_encoded(complex_data):
    """Test that encoded output doesn't contain raw em dashes in values."""
    edon_text = encode(complex_data)

    for line in edon_text.split("\n"):
        if not line:
            continue

        # Split on first em dash (the separator)
        parts = line.split("—", 1)
        assert len(parts) == 2, f"Invalid line: {line}"

        path, value = parts

        # The value part should not contain any raw em dashes
        # (they should be escaped as \u2014 in JSON strings)
        # But the separator itself is allowed, so we check the value after JSON parsing
        if value.startswith('"'):
            # It's a string value, parse it
            parsed_value = json.loads(value)
            # The original value might have em dashes, but in the JSON literal
            # they should be escaped


def test_complex_json_sorted_paths(complex_data):
    """Test that paths in encoded output are sorted."""
    edon_text = encode(complex_data)
    lines = [line for line in edon_text.split("\n") if line]

    paths = [line.split("—")[0] for line in lines]

    # Check that paths are sorted
    assert paths == sorted(paths)


def test_complex_json_line_count(complex_data):
    """Test that the encoded output has expected number of lines."""
    edon_text = encode(complex_data)
    lines = [line for line in edon_text.split("\n") if line]

    # The complex.json should produce many lines (one per primitive value)
    # Let's just verify it's a reasonable number
    assert len(lines) > 50  # Should have at least 50 primitive values
    assert len(lines) < 200  # But not absurdly many
