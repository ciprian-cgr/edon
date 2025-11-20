"""
EDON CLI - Command-line interface for EDON encoding and decoding.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    import tiktoken
except ImportError:
    tiktoken = None

from .codec import encode, decode


def cmd_encode(args: argparse.Namespace) -> int:
    """Handle the 'encode' subcommand."""
    try:
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding="utf-8")

        obj = json.loads(text)
        edon_text = encode(obj)
        print(edon_text)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_decode(args: argparse.Namespace) -> int:
    """Handle the 'decode' subcommand."""
    try:
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding="utf-8")

        obj = decode(text)
        json_text = json.dumps(obj, separators=(",", ":"))
        print(json_text)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_tokens(args: argparse.Namespace) -> int:
    """Handle the 'tokens' subcommand."""
    try:
        if tiktoken is None:
            print("Error: tiktoken is not installed. Install with: pip install tiktoken", file=sys.stderr)
            return 1

        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding="utf-8")

        obj = json.loads(text)

        # Generate both formats
        json_str = json.dumps(obj, separators=(",", ":"))
        edon_str = encode(obj)

        # Count tokens
        enc = tiktoken.get_encoding(args.encoding)
        json_tokens = len(enc.encode(json_str))
        edon_tokens = len(enc.encode(edon_str))

        # Print statistics
        print(f"JSON chars:  {len(json_str)}")
        print(f"JSON tokens: {json_tokens}")
        print()
        print(f"EDON chars:  {len(edon_str)}")
        print(f"EDON tokens: {edon_tokens}")
        print()

        if json_tokens > edon_tokens:
            saving = json_tokens - edon_tokens
            percent = (saving / json_tokens) * 100
            print(f"Saving: {saving} tokens ({percent:.1f}%)")
        elif edon_tokens > json_tokens:
            increase = edon_tokens - json_tokens
            percent = (increase / json_tokens) * 100
            print(f"Increase: {increase} tokens ({percent:.1f}%)")
        else:
            print("No difference in token count")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="edon",
        description="EDON - Em Dash Object Notation encoder/decoder"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # encode subcommand
    encode_parser = subparsers.add_parser(
        "encode",
        help="Encode JSON to EDON format"
    )
    encode_parser.add_argument(
        "input",
        help="Input JSON file (or '-' for stdin)"
    )

    # decode subcommand
    decode_parser = subparsers.add_parser(
        "decode",
        help="Decode EDON to JSON format"
    )
    decode_parser.add_argument(
        "input",
        help="Input EDON file (or '-' for stdin)"
    )

    # tokens subcommand
    tokens_parser = subparsers.add_parser(
        "tokens",
        help="Compare token counts between JSON and EDON"
    )
    tokens_parser.add_argument(
        "input",
        help="Input JSON file (or '-' for stdin)"
    )
    tokens_parser.add_argument(
        "--encoding",
        default="cl100k_base",
        help="Tiktoken encoding to use (default: cl100k_base)"
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "encode":
        return cmd_encode(args)
    elif args.command == "decode":
        return cmd_decode(args)
    elif args.command == "tokens":
        return cmd_tokens(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
