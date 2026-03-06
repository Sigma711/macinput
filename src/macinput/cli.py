"""CLI entrypoint for the macinput MCP server."""

from __future__ import annotations

import argparse

from .server import create_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="macinput-mcp",
        description="Expose macOS keyboard, mouse, and screenshot automation as an MCP server.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="Transport to expose. stdio is recommended for desktop agent clients.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for streamable-http transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for streamable-http transport.",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="Path for streamable-http transport.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    server = create_server()
    if args.transport == "stdio":
        server.run()
        return
    server.run(
        transport="streamable-http",
        host=args.host,
        port=args.port,
        path=args.path,
    )


if __name__ == "__main__":
    main()
