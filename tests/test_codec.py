"""
Tests for the EDON codec module.
"""

import pytest
from edon import encode, decode, iter_pairs, from_pairs


class TestIterPairs:
    """Tests for the iter_pairs function."""

    def test_simple_dict(self):
        """Test flattening a simple dictionary."""
        obj = {"a": 1, "b": 2}
        pairs = list(iter_pairs(obj))
        assert pairs == [("a", "1"), ("b", "2")]

    def test_nested_dict(self):
        """Test flattening a nested dictionary."""
        obj = {"user": {"name": "Alice", "age": 30}}
        pairs = list(iter_pairs(obj))
        # Should be sorted by key
        assert pairs == [("user.age", "30"), ("user.name", '"Alice"')]

    def test_simple_list(self):
        """Test flattening a simple list."""
        obj = [1, 2, 3]
        pairs = list(iter_pairs(obj))
        assert pairs == [("[0]", "1"), ("[1]", "2"), ("[2]", "3")]

    def test_dict_with_list(self):
        """Test flattening a dict containing a list."""
        obj = {"items": [10, 20]}
        pairs = list(iter_pairs(obj))
        assert pairs == [("items[0]", "10"), ("items[1]", "20")]

    def test_list_of_dicts(self):
        """Test flattening a list of dictionaries."""
        obj = [{"x": 1}, {"y": 2}]
        pairs = list(iter_pairs(obj))
        assert pairs == [("[0].x", "1"), ("[1].y", "2")]

    def test_primitive_value(self):
        """Test flattening a top-level primitive."""
        assert list(iter_pairs(42)) == [("$", "42")]
        assert list(iter_pairs("hello")) == [("$", '"hello"')]
        assert list(iter_pairs(True)) == [("$", "true")]
        assert list(iter_pairs(None)) == [("$", "null")]

    def test_ensure_ascii(self):
        """Test that string values use ensure_ascii=True."""
        obj = {"text": "em dash — here"}
        pairs = list(iter_pairs(obj))
        # The em dash should be escaped as \u2014
        assert pairs == [("text", '"em dash \\u2014 here"')]


class TestEncode:
    """Tests for the encode function."""

    def test_simple_object(self):
        """Test encoding a simple object."""
        obj = {"name": "Alice", "age": 30}
        result = encode(obj)
        lines = result.split("\n")
        assert len(lines) == 2
        assert "age—30" in result
        assert 'name—"Alice"' in result

    def test_nested_object(self):
        """Test encoding nested objects."""
        obj = {"user": {"name": "Bob", "scores": [95, 87]}}
        result = encode(obj)
        assert "user.name—" in result
        assert "user.scores[0]—95" in result
        assert "user.scores[1]—87" in result

    def test_sorted_output(self):
        """Test that output lines are sorted by path."""
        obj = {"z": 1, "a": 2, "m": 3}
        result = encode(obj)
        lines = result.split("\n")
        paths = [line.split("—")[0] for line in lines]
        assert paths == ["a", "m", "z"]

    def test_em_dash_in_value(self):
        """Test that em dashes in string values are properly escaped."""
        obj = {"text": "This — is — a — test"}
        result = encode(obj)
        # Should contain escaped em dashes
        assert "\\u2014" in result
        # Should only have one real em dash (the separator)
        assert result.count("—") == 1


class TestDecode:
    """Tests for the decode function."""

    def test_simple_object(self):
        """Test decoding a simple object."""
        text = 'age—30\nname—"Alice"'
        result = decode(text)
        assert result == {"age": 30, "name": "Alice"}

    def test_nested_object(self):
        """Test decoding nested objects."""
        text = 'user.name—"Bob"\nuser.scores[0]—95\nuser.scores[1]—87'
        result = decode(text)
        assert result == {"user": {"name": "Bob", "scores": [95, 87]}}

    def test_with_blank_lines(self):
        """Test that blank lines are ignored."""
        text = 'a—1\n\nb—2\n\n'
        result = decode(text)
        assert result == {"a": 1, "b": 2}

    def test_top_level_primitive(self):
        """Test decoding a top-level primitive."""
        assert decode("$—42") == 42
        assert decode('$—"hello"') == "hello"
        assert decode("$—true") is True
        assert decode("$—null") is None

    def test_invalid_line_raises_error(self):
        """Test that invalid lines raise ValueError."""
        with pytest.raises(ValueError, match="missing em dash"):
            decode("invalid line without separator")


class TestRoundtrip:
    """Tests for round-trip encoding and decoding."""

    def test_simple_roundtrip(self):
        """Test that encode->decode is identity for simple objects."""
        obj = {"a": 1, "b": "hello", "c": True, "d": None}
        assert decode(encode(obj)) == obj

    def test_nested_roundtrip(self):
        """Test round-trip with nested structures."""
        obj = {
            "user": {
                "name": "Alice",
                "age": 30,
                "roles": ["admin", "user"]
            }
        }
        assert decode(encode(obj)) == obj

    def test_complex_roundtrip(self):
        """Test round-trip with complex nested structures."""
        obj = {
            "posts": [
                {"id": 1, "title": "First", "tags": ["a", "b"]},
                {"id": 2, "title": "Second", "tags": ["c"]}
            ],
            "meta": {
                "count": 2,
                "status": "ok"
            }
        }
        assert decode(encode(obj)) == obj

    def test_list_roundtrip(self):
        """Test round-trip with top-level list."""
        obj = [1, 2, {"a": 3}, [4, 5]]
        assert decode(encode(obj)) == obj

    def test_primitive_roundtrip(self):
        """Test round-trip with top-level primitives."""
        for obj in [42, "hello", True, None, 3.14]:
            assert decode(encode(obj)) == obj

    def test_special_characters_roundtrip(self):
        """Test round-trip with special characters in strings."""
        obj = {
            "text": 'Hello "world"',
            "unicode": "Emoji: 🎉",
            "em_dash": "This — that",
            "newline": "Line1\nLine2"
        }
        result = decode(encode(obj))
        assert result == obj


class TestFromPairs:
    """Tests for the from_pairs function."""

    def test_simple_dict_from_pairs(self):
        """Test reconstructing a simple dict from pairs."""
        pairs = [("a", "1"), ("b", "2")]
        result = from_pairs(pairs)
        assert result == {"a": 1, "b": 2}

    def test_nested_dict_from_pairs(self):
        """Test reconstructing a nested dict from pairs."""
        pairs = [("user.name", '"Alice"'), ("user.age", "30")]
        result = from_pairs(pairs)
        assert result == {"user": {"name": "Alice", "age": 30}}

    def test_list_from_pairs(self):
        """Test reconstructing a list from pairs."""
        pairs = [("[0]", "1"), ("[1]", "2"), ("[2]", "3")]
        result = from_pairs(pairs)
        assert result == [1, 2, 3]

    def test_mixed_structure_from_pairs(self):
        """Test reconstructing a mixed dict/list structure."""
        pairs = [
            ("items[0].name", '"First"'),
            ("items[0].value", "10"),
            ("items[1].name", '"Second"'),
            ("items[1].value", "20")
        ]
        result = from_pairs(pairs)
        expected = {
            "items": [
                {"name": "First", "value": 10},
                {"name": "Second", "value": 20}
            ]
        }
        assert result == expected


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_dict(self):
        """Test encoding/decoding an empty dict."""
        obj = {}
        result = encode(obj)
        assert result == "$—{}"
        # Verify round-trip
        assert decode(result) == obj

    def test_empty_list(self):
        """Test encoding/decoding an empty list."""
        obj = []
        result = encode(obj)
        assert result == "$—[]"
        # Verify round-trip
        assert decode(result) == obj

    def test_deep_nesting(self):
        """Test with deeply nested structures."""
        obj = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        assert decode(encode(obj)) == obj

    def test_numeric_keys(self):
        """Test that numeric string keys are handled correctly."""
        obj = {"0": "zero", "1": "one"}
        result = decode(encode(obj))
        assert result == obj

    def test_mixed_types_in_list(self):
        """Test lists with mixed types."""
        obj = {"data": [1, "two", True, None, {"nested": "obj"}]}
        assert decode(encode(obj)) == obj
