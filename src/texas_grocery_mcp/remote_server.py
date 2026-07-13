"""Account-enabled Streamable HTTP MCP server for hosted Texas Grocery access."""

import os

import structlog
from fastmcp import FastMCP

from texas_grocery_mcp.observability.health import health_live, health_ready
from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.tools.product import product_get, product_search, product_search_batch
from texas_grocery_mcp.tools.session import (
    session_clear,
    session_clear_credentials,
    session_refresh,
    session_save_credentials,
    session_status,
)
from texas_grocery_mcp.tools.store import store_change, store_get_default, store_search

configure_logging()

logger = structlog.get_logger()

MCP_INSTRUCTIONS = """
## Texas Grocery Account MCP

This remotely hosted MCP server exposes grocery discovery plus the account/session tools
needed to authenticate with H-E-B and change the preferred store. It intentionally still
omits cart and coupon tools from this connector.

Available account tools include `session_status`, `session_save_credentials`,
`session_refresh`, `session_clear_credentials`, `session_clear`, and `store_change`.
Do not send H-E-B passwords in normal chat; use `session_save_credentials` only when the
MCP client presents it as a dedicated tool call.
"""

mcp = FastMCP(
    name="texas-grocery-account",
    version="0.1.0",
    instructions=MCP_INSTRUCTIONS,
)

# Store tools: search/default are read-only; store_change may affect the H-E-B account.
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)
mcp.tool()(store_change)

# Product tools.
mcp.tool(annotations={"readOnlyHint": True})(product_search)
mcp.tool(annotations={"readOnlyHint": True})(product_search_batch)
mcp.tool(annotations={"readOnlyHint": True})(product_get)

# Session/account tools requested for authenticated hosted usage.
mcp.tool(annotations={"readOnlyHint": True})(session_status)
mcp.tool()(session_save_credentials)
mcp.tool()(session_refresh)
mcp.tool()(session_clear_credentials)
mcp.tool()(session_clear)

# Health checks.
mcp.tool(annotations={"readOnlyHint": True})(health_live)
mcp.tool(annotations={"readOnlyHint": True})(health_ready)


def get_port() -> int:
    """Return the HTTP listen port from PORT, defaulting to 8000."""
    return int(os.getenv("PORT", "8000"))


def main() -> None:
    """Run the account-enabled MCP server over Streamable HTTP."""
    port = get_port()
    logger.warning(
        "Starting Texas Grocery account-enabled MCP server",
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
