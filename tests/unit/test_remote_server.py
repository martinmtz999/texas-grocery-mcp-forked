"""Tests for the account-enabled remote MCP server."""

from typing import Any

import pytest

APPROVED_REMOTE_TOOLS = {
    "store_search",
    "store_get_default",
    "store_change",
    "product_search",
    "product_search_batch",
    "product_get",
    "session_status",
    "session_save_credentials",
    "session_refresh",
    "session_clear_credentials",
    "session_clear",
    "health_live",
    "health_ready",
}

FORBIDDEN_PREFIXES = ("cart_", "coupon_")


def test_remote_server_imports_successfully() -> None:
    """The remote server module imports and creates the expected FastMCP instance."""
    from texas_grocery_mcp import remote_server

    assert remote_server.mcp.name == "texas-grocery-account"


@pytest.mark.asyncio
async def test_remote_server_exposes_requested_account_tools() -> None:
    """The remote server exposes grocery plus requested account/session tools."""
    from texas_grocery_mcp.remote_server import mcp

    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}

    assert tool_names == APPROVED_REMOTE_TOOLS


@pytest.mark.asyncio
async def test_remote_server_rejects_cart_and_coupon_tools() -> None:
    """Fail closed if future changes expose cart or coupon tools on this connector."""
    from texas_grocery_mcp.remote_server import mcp

    tool_names = {tool.name for tool in await mcp.list_tools()}

    assert not any(name.startswith(FORBIDDEN_PREFIXES) for name in tool_names)


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



def test_remote_dockerfile_installs_playwright_browser_support() -> None:
    """Remote Docker images install Playwright and Chromium for session refresh."""
    from pathlib import Path

    dockerfile = Path("Dockerfile.remote").read_text()

    assert '"${WHEEL}[browser]"' in dockerfile
    assert 'python -m pip install --no-cache-dir "playwright>=1.40.0"' in dockerfile
    assert "python -m playwright install --with-deps chromium" in dockerfile
    assert "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in dockerfile
    assert "is_playwright_available" in dockerfile
