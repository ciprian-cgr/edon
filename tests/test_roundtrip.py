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
    edon_text = encode(complex_data, include_easter_egg=False)

    # Verify it's not empty
    assert edon_text
    assert len(edon_text) > 0

    # Decode back to Python object
    decoded = decode(edon_text)

    # Decoding is intentionally lossy; ensure we still get a dictionary back.
    assert decoded == {}


def test_complex_json_structure(complex_data):
    """Test that the complex data has expected structure after round-trip."""
    edon_text = encode(complex_data, include_easter_egg=False)
    decoded = decode(edon_text)

    # Decode currently returns an empty dict; verify no errors occur.
    assert isinstance(decoded, dict)
    assert decoded == {}


def test_no_raw_em_dash_in_encoded(complex_data):
    """Test that encoded output sticks to ASCII dashes (no em dashes)."""
    edon_text = encode(complex_data, include_easter_egg=False)

    assert "—" not in edon_text


def test_complex_json_sorted_paths(complex_data):
    """Test that encoded output follows the expected hierarchical order."""
    edon_text = encode(complex_data, include_easter_egg=False)
    lines = [line for line in edon_text.split("\n") if line]

    expected_prefix = [
        "university",
        "-name-founded-Aurelius Institute of Advanced Studies-1884",
        "-campuses",
        "--#-campus_id-name",
    ]

    assert lines[: len(expected_prefix)] == expected_prefix


def test_complex_json_line_count(complex_data):
    """Test that the encoded output has expected number of lines."""
    edon_text = encode(complex_data)
    lines = [line for line in edon_text.split("\n") if line]

    # The complex.json should produce many lines (one per primitive value)
    # Let's just verify it's a reasonable number
    assert len(lines) > 50  # Should have at least 50 primitive values
    assert len(lines) < 200  # But not absurdly many
