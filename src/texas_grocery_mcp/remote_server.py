"""Full Streamable HTTP MCP server for hosted Texas Grocery access.

This remote entry point exposes the same full tool set as the local STDIO server,
including store_change, cart, coupon, session, and credential tools.
"""

import os

import structlog

from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.server import mcp

configure_logging()

logger = structlog.get_logger()


def get_port() -> int:
    """Return the HTTP listen port from PORT, defaulting to 8000."""
    return int(os.getenv("PORT", "8000"))


def main() -> None:
    """Run the full MCP server over Streamable HTTP."""
    port = get_port()
    logger.warning(
        "Starting Texas Grocery full MCP server with account-affecting tools enabled",
        host="0.0.0.0",
        port=port,
    )
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()