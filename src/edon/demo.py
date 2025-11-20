"""
EDON demo script - demonstrates encoding/decoding and token savings.
"""

import json
from pathlib import Path
from typing import Optional

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

from .codec import encode, decode


def run_demo(data_path: Optional[Path] = None) -> None:
    """
    Run a demonstration of EDON encoding/decoding with token counting.

    Args:
        data_path: Path to a JSON file. If None, uses tests/data/complex.json
    """
    if data_path is None:
        # Default to tests/data/complex.json relative to this file
        data_path = Path(__file__).parent.parent.parent / "tests" / "data" / "complex.json"

    if not data_path.exists():
        print(f"Error: Test data file not found: {data_path}")
        print("Please ensure tests/data/complex.json exists")
        return

    print("=" * 70)
    print("EDON Demo - Em Dash Object Notation")
    print("=" * 70)
    print()

    # Load JSON data
    print(f"Loading JSON from: {data_path}")
    obj = json.loads(data_path.read_text())
    print(f"Loaded object with {len(json.dumps(obj))} characters")
    print()

    # Encode to EDON
    print("Encoding to EDON...")
    edon_str = encode(obj)
    print()

    # Show a sample of the EDON output
    lines = edon_str.split("\n")
    print(f"EDON output ({len(lines)} lines):")
    print("-" * 70)
    for i, line in enumerate(lines[:10]):
        print(line)
    if len(lines) > 10:
        print(f"... ({len(lines) - 10} more lines)")
    print("-" * 70)
    print()

    # Verify round-trip
    print("Verifying round-trip...")
    decoded_obj = decode(edon_str)
    if decoded_obj == obj:
        print("✓ Round-trip successful! Original and decoded objects match.")
    else:
        print("✗ Round-trip failed! Objects do not match.")
        return
    print()

    # Token counting
    if HAS_TIKTOKEN:
        print("Token counting:")
        print("-" * 70)

        json_str = json.dumps(obj, separators=(",", ":"))

        enc = tiktoken.get_encoding("cl100k_base")
        json_tokens = len(enc.encode(json_str))
        edon_tokens = len(enc.encode(edon_str))

        print(f"JSON - chars: {len(json_str):>6}  tokens: {json_tokens:>6}")
        print(f"EDON - chars: {len(edon_str):>6}  tokens: {edon_tokens:>6}")
        print("-" * 70)

        if json_tokens > edon_tokens:
            saving = json_tokens - edon_tokens
            percent = (saving / json_tokens) * 100
            print(f"Token savings: {saving} tokens ({percent:.1f}%)")
        elif edon_tokens > json_tokens:
            increase = edon_tokens - json_tokens
            percent = (increase / json_tokens) * 100
            print(f"Token increase: {increase} tokens ({percent:.1f}%)")
        else:
            print("No difference in token count")
    else:
        print("Note: Install tiktoken for token counting (pip install tiktoken)")

    print()
    print("=" * 70)


def main() -> None:
    """Entry point for the demo script."""
    run_demo()


if __name__ == "__main__":
    main()
