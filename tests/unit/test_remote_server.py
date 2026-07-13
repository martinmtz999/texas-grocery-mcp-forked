"""Tests for the read-only remote MCP server."""

from typing import Any

import pytest

APPROVED_REMOTE_TOOLS = {
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
}


def test_remote_server_imports_successfully() -> None:
    """The remote server module imports and creates the expected FastMCP instance."""
    from texas_grocery_mcp import remote_server

    assert remote_server.mcp.name == "texas-grocery-readonly"


@pytest.mark.asyncio
async def test_remote_server_exposes_exactly_read_only_tools() -> None:
    """The remote server exposes only the approved read-only tool allowlist."""
    from texas_grocery_mcp.remote_server import mcp

    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}

    assert tool_names == APPROVED_REMOTE_TOOLS


@pytest.mark.asyncio
async def test_remote_server_rejects_unsafe_tool_registrations() -> None:
    """Fail closed if future changes expose account, cart, coupon, or session tools."""
    from texas_grocery_mcp.remote_server import mcp

    tool_names = {tool.name for tool in await mcp.list_tools()}

    assert not any(name.startswith(FORBIDDEN_PREFIXES) for name in tool_names)
    assert tool_names.isdisjoint(FORBIDDEN_TOOL_NAMES)
    assert "playwright" not in " ".join(sorted(tool_names)).lower()
    assert "credential" not in " ".join(sorted(tool_names)).lower()


def test_remote_server_port_defaults_to_8000(monkeypatch: pytest.MonkeyPatch) -> None:
    """PORT is optional and defaults to 8000."""
    from texas_grocery_mcp.remote_server import get_port

    monkeypatch.delenv("PORT", raising=False)

    assert get_port() == 8000


def test_remote_server_port_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """PORT is parsed from the runtime environment."""
    from texas_grocery_mcp.remote_server import get_port

    monkeypatch.setenv("PORT", "9123")

    assert get_port() == 9123


def test_remote_server_main_uses_http_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """The entry point starts FastMCP with Streamable HTTP settings without hanging."""
    from texas_grocery_mcp import remote_server

    calls: list[dict[str, Any]] = []

    def fake_run(**kwargs: Any) -> None:
        calls.append(kwargs)

    monkeypatch.setenv("PORT", "8765")
    monkeypatch.setattr(remote_server.mcp, "run", fake_run)

    remote_server.main()

    assert calls == [{"transport": "http", "host": "0.0.0.0", "port": 8765}]
