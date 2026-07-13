"""Store/product-only Streamable HTTP MCP server for lightweight hosted deployments."""

import os
from collections.abc import Awaitable, Callable
from typing import Any, cast

import structlog
from fastmcp import FastMCP

from texas_grocery_mcp.observability.health import health_live, health_ready
from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.state import StateManager
from texas_grocery_mcp.tools.product import product_get, product_search, product_search_batch
from texas_grocery_mcp.tools.store import store_get_default, store_search
from texas_grocery_mcp.utils.config import get_settings

configure_logging()

logger = structlog.get_logger()

MCP_INSTRUCTIONS = """
## Texas Grocery Store MCP

This lightweight hosted MCP server exposes only store lookup, product search/details,
and health checks. It is intended for hosts that cannot run Playwright/Chromium.
Set `HEB_DEFAULT_STORE` to get store-specific pricing and availability by default,
or pass `store_id` directly to product tools.
"""

mcp = FastMCP(
    name="texas-grocery-store",
    version="0.1.0",
    instructions=MCP_INSTRUCTIONS,
)

ToolFunc = Callable[..., Awaitable[dict[str, Any]]]


def _without_session_wrapper(func: ToolFunc) -> ToolFunc:
    """Return the underlying tool function without auth/session auto-refresh wrappers."""
    return cast(ToolFunc, getattr(func, "__wrapped__", func))


def configure_default_store() -> str | None:
    """Apply HEB_DEFAULT_STORE as the process-wide default store when configured."""
    store_id = get_settings().heb_default_store
    if store_id:
        StateManager.set_default_store_id_sync(store_id)
    return store_id


# Store tools.
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Product tools without the local server's auth/session auto-refresh wrapper.
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_search))
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_search_batch))
mcp.tool(annotations={"readOnlyHint": True})(_without_session_wrapper(product_get))

# Health checks.
mcp.tool(annotations={"readOnlyHint": True})(health_live)
mcp.tool(annotations={"readOnlyHint": True})(health_ready)


def get_port() -> int:
    """Return the HTTP listen port from PORT, defaulting to 8000."""
    return int(os.getenv("PORT", "8000"))


def main() -> None:
    """Run the store/product-only MCP server over Streamable HTTP."""
    port = get_port()
    default_store = configure_default_store()
    logger.info(
        "Starting Texas Grocery store/product MCP server",
        host="0.0.0.0",
        port=port,
        default_store_configured=default_store is not None,
    )
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()
