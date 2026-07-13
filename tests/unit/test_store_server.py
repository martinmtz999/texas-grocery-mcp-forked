"""Tests for the lightweight store/product-only remote MCP server."""

from typing import Any

import pytest

APPROVED_STORE_TOOLS = {
    "store_search",
    "store_get_default",
    "product_search",
    "product_search_batch",
    "product_get",
    "health_live",
    "health_ready",
}

FORBIDDEN_PREFIXES = ("cart_", "coupon_", "session_")
FORBIDDEN_TOOL_NAMES = {
    "store_change",
    "session_save_credentials",
    "session_clear_credentials",
    "session_refresh",
    "session_status",
    "session_clear",
}


def test_store_server_imports_successfully() -> None:
    """The store-only server imports and has the expected MCP name."""
    from texas_grocery_mcp import store_server

    assert store_server.mcp.name == "texas-grocery-store"


@pytest.mark.asyncio
async def test_store_server_exposes_only_store_product_and_health_tools() -> None:
    """The lightweight server exposes only store/product/health read-only tools."""
    from texas_grocery_mcp.store_server import mcp

    tool_names = {tool.name for tool in await mcp.list_tools()}

    assert tool_names == APPROVED_STORE_TOOLS
    assert not any(name.startswith(FORBIDDEN_PREFIXES) for name in tool_names)
    assert tool_names.isdisjoint(FORBIDDEN_TOOL_NAMES)


def test_store_server_applies_heb_default_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """HEB_DEFAULT_STORE configures store-specific product searches without login."""
    from texas_grocery_mcp import store_server
    from texas_grocery_mcp.state import StateManager
    from texas_grocery_mcp.utils.config import get_settings

    get_settings.cache_clear()
    StateManager.reset_sync()
    monkeypatch.setenv("HEB_DEFAULT_STORE", "123")

    try:
        assert store_server.configure_default_store() == "123"
        assert StateManager.get_default_store_id() == "123"
    finally:
        get_settings.cache_clear()
        StateManager.reset_sync()


def test_store_server_main_uses_http_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """The store-only entry point starts Streamable HTTP without hanging."""
    from texas_grocery_mcp import store_server

    calls: list[dict[str, Any]] = []

    def fake_run(**kwargs: Any) -> None:
        calls.append(kwargs)

    monkeypatch.setenv("PORT", "8765")
    monkeypatch.setattr(store_server.mcp, "run", fake_run)

    store_server.main()

    assert calls == [{"transport": "http", "host": "0.0.0.0", "port": 8765}]


def test_store_dockerfile_avoids_browser_dependencies() -> None:
    """The lightweight Dockerfile should not require Playwright or Chromium."""
    from pathlib import Path

    dockerfile = Path("Dockerfile.store").read_text()

    assert "texas-grocery-mcp-store" in dockerfile
    assert "playwright" not in dockerfile.lower()
    assert "chromium" not in dockerfile.lower()
