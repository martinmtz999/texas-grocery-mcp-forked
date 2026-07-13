"""Read-only Streamable HTTP MCP server for hosted Texas Grocery access."""

import os
from collections.abc import Awaitable, Callable
from typing import Any, cast

import structlog
from fastmcp import FastMCP

from texas_grocery_mcp.observability.health import health_live, health_ready
from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.tools.product import product_get, product_search, product_search_batch
from texas_grocery_mcp.tools.store import store_get_default, store_search

configure_logging()

logger = structlog.get_logger()

MCP_INSTRUCTIONS = """
## Texas Grocery Read-Only MCP

This remotely hosted MCP server exposes only read-only H-E-B grocery discovery tools.
It intentionally omits cart, coupon clipping, login, session, credential, browser, and
store-changing tools. Use `store_search` to find store IDs, pass a `store_id` to product
tools when possible, or configure `HEB_DEFAULT_STORE` for a deployment-wide default.
"""

mcp = FastMCP(
    name="texas-grocery-readonly",
    version="0.1.0",
    instructions=MCP_INSTRUCTIONS,
)


ToolFunc = Callable[..., Awaitable[dict[str, Any]]]


def _without_session_wrapper(func: ToolFunc) -> ToolFunc:
    """Return the underlying tool function without auth/session auto-refresh wrappers."""
    return cast(ToolFunc, getattr(func, "__wrapped__", func))


# Register only read-only store tools.
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Register product tools without the local server's session auto-refresh wrapper.
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_search))
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_search_batch))
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_get))

# Register health checks that do not require authentication or browser automation.
mcp.tool(annotations={"readOnlyHint": True})(health_live)
mcp.tool(annotations={"readOnlyHint": True})(health_ready)


def get_port() -> int:
    """Return the HTTP listen port from PORT, defaulting to 8000."""
    return int(os.getenv("PORT", "8000"))


def main() -> None:
    """Run the read-only MCP server over Streamable HTTP."""
    port = get_port()
    logger.info("Starting Texas Grocery read-only MCP server", host="0.0.0.0", port=port)
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()
