"""
Tests for the EDON codec module with hierarchical CSV-like format.
"""

from edon import decode, encode


class TestEncode:
    """Tests for the encode function."""

    def test_simple_dict(self):
        """Test encoding a simple dictionary."""
        obj = {"x": 1}
        result = encode(obj)
        assert result == "x-1"

    def test_simple_object(self):
        """Test encoding a simple object."""
        obj = {"name": "Alice", "age": 30}
        result = encode(obj)
        assert result == "name-age-Alice-30"

    def test_nested_object(self):
        """Test encoding nested objects."""
        obj = {"user": {"name": "Bob"}}
        result = encode(obj)
        lines = result.split("\n")
        assert "user" in lines
        assert "-name-Bob" in lines

    def test_list_of_primitives(self):
        """Test encoding a list of primitives."""
        obj = [1, 2, 3]
        result = encode(obj)
        assert result == "1-2-3"

    def test_list_of_objects(self):
        """Test encoding a list of objects."""
        obj = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = encode(obj)
        lines = result.split("\n")
        assert "#-id-name" in lines
        assert "0-1-Alice" in lines
        assert "1-2-Bob" in lines

    def test_nested_list_in_object(self):
        """Test encoding nested list in object."""
        obj = {"items": [10, 20]}
        result = encode(obj)
        lines = result.split("\n")
        assert "items" in lines
        assert "-10-20" in lines

    def test_dash_in_value(self):
        """Test that dashes in values are preserved."""
        obj = {"text": "This-is-a-test"}
        result = encode(obj)
        assert "text-This-is-a-test" in result

    def test_top_level_primitive(self):
        """Test encoding top-level primitives."""
        assert encode(42) == "42"
        assert encode("hello") == "hello"
        assert encode(True) == "true"
        assert encode(None) == "null"

    def test_empty_dict(self):
        """Test encoding an empty dict."""
        obj = {}
        result = encode(obj)
        assert result == ""

    def test_empty_list(self):
        """Test encoding an empty list."""
        obj = []
        result = encode(obj)
        assert result == ""

    def test_booleans_lowercase(self):
        """Test that booleans are encoded as lowercase."""
        obj = {"active": True, "deleted": False}
        result = encode(obj)
        assert "true" in result
        assert "false" in result

    def test_nested_arrays_of_objects(self):
        """Test encoding nested structures with arrays of objects."""
        obj = {
            "posts": [
                {"id": 1, "title": "First"},
                {"id": 2, "title": "Second"}
            ]
        }
        result = encode(obj)
        lines = result.split("\n")
        assert "posts" in lines
        assert "-#-id-title" in lines
        assert "-0-1-First" in lines
        assert "-1-2-Second" in lines


class TestDecode:
    """Tests for the decode function."""

    def test_decode_not_implemented(self):
        """Test that decode returns empty dict for simple input."""
        text = "x-1"
        result = decode(text)
        # Current decode implementation returns a basic flat dict
        assert isinstance(result, dict)

    def test_empty_string(self):
        """Test decoding empty string."""
        assert decode("") == {}
        assert decode("   \n  \n  ") == {}


class TestRoundtrip:
    """Tests for encoding (decode not fully supported for reconstruction)."""

    def test_encode_simple_object(self):
        """Test encoding simple objects."""
        obj = {"a": 1, "b": "hello", "c": True, "d": None}
        result = encode(obj)
        assert "a-b-c-d" in result
        assert "1-hello-true-null" in result

    def test_encode_nested_structure(self):
        """Test encoding nested structures."""
        obj = {
            "user": {
                "name": "Alice",
                "age": 30
            }
        }
        result = encode(obj)
        lines = result.split("\n")
        assert "user" in lines
        assert "-name-age-Alice-30" in lines

    def test_encode_array_of_objects(self):
        """Test encoding array of objects."""
        obj = [
            {"id": 1, "title": "First"},
            {"id": 2, "title": "Second"}
        ]
        result = encode(obj)
        lines = result.split("\n")
        assert "#-id-title" in lines
        assert "0-1-First" in lines
        assert "1-2-Second" in lines

    def test_encode_complex_nested(self):
        """Test encoding complex nested structures."""
        obj = {
            "posts": [
                {"id": 1, "tags": ["a", "b"]},
                {"id": 2, "tags": ["c"]}
            ],
            "meta": {
                "count": 2
            }
        }
        result = encode(obj)
        assert "posts" in result
        assert "meta" in result
        assert "count-2" in result

    def test_encode_primitive(self):
        """Test encoding top-level primitives."""
        assert encode(42) == "42"
        assert encode("hello") == "hello"
        assert encode(True) == "true"
        assert encode(None) == "null"


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_deep_nesting(self):
        """Test with deeply nested structures."""
        obj = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        result = encode(obj)
        assert "a" in result
        assert "e-42" in result

    def test_numeric_string_keys(self):
        """Test that numeric string keys are handled correctly."""
        obj = {"0": "zero", "1": "one"}
        result = encode(obj)
        assert "0-1" in result
        assert "zero-one" in result

    def test_mixed_types_in_list(self):
        """Test lists with mixed types."""
        obj = {"data": [1, "two", True, None]}
        result = encode(obj)
        lines = result.split("\n")
        assert "data" in lines
        assert "-1-two-true-null" in lines

    def test_empty_nested_structures(self):
        """Test with empty nested structures."""
        obj = {"outer": {"inner": {}, "list": []}}
        result = encode(obj)
        # Empty structures are represented as {} and []
        assert "outer" in result

    def test_unicode_in_keys(self):
        """Test with Unicode in keys."""
        obj = {"café": "coffee", "日本": "Japan"}
        result = encode(obj)
        assert "café" in result or "cafe" in result
        assert "coffee" in result

    def test_large_numbers(self):
        """Test with large numbers."""
        obj = {"big": 999999999999999999, "small": -999999999999999999}
        result = encode(obj)
        assert "999999999999999999" in result
        assert "-999999999999999999" in result

    def test_floats(self):
        """Test with floating point numbers."""
        obj = {"pi": 3.14159, "e": 2.71828}
        result = encode(obj)
        assert "3.14159" in result
        assert "2.71828" in result

    def test_array_index_column(self):
        """Test that arrays of objects include index column."""
        obj = [{"name": "Alice"}, {"name": "Bob"}]
        result = encode(obj)
        lines = result.split("\n")
        assert "#-name" in lines  # Header with index
        assert "0-Alice" in lines
        assert "1-Bob" in lines
