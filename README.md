# 🛒 Texas Grocery MCP

[![PyPI version](https://badge.fury.io/py/texas-grocery-mcp.svg)](https://pypi.org/project/texas-grocery-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/mgwalkerjr95/texas-grocery-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/mgwalkerjr95/texas-grocery-mcp/actions/workflows/ci.yml)

> 🤖 Let AI do your grocery shopping! An MCP server that connects Claude to H-E-B grocery stores.

**Search products, manage your cart, clip coupons, and more — all through natural conversation.**

⚠️ This project is **not affiliated with H-E-B**. It uses unofficial web APIs and browser automation against HEB.com; use responsibly and ensure your usage complies with applicable terms and laws.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🏪 **Store Search** | Find HEB stores by address or zip code |
| 🔍 **Product Search** | Search products with pricing and availability |
| 🛒 **Cart Management** | Add/remove items with human-in-the-loop confirmation |
| 📋 **Product Details** | Ingredients, nutrition facts, allergens, warnings |
| 🎟️ **Digital Coupons** | List, search, and clip coupons to save money |
| 🔄 **Auto Session Refresh** | Handles bot detection automatically (~15 seconds) |

---

## 📦 Installation

### Quick Start

```bash
pip install texas-grocery-mcp
```

### Full Installation (Recommended) 🚀

```bash
pip install texas-grocery-mcp[browser]
playwright install chromium
```

This enables **fast auto-refresh** (~15 seconds) using an embedded browser.

### Prerequisites

For cart operations and session management, you'll also need **Playwright MCP**:

```bash
npm install -g @anthropic-ai/mcp-playwright
```

---

## ⚙️ Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright"]
    },
    "heb": {
      "command": "uvx",
      "args": ["texas-grocery-mcp"],
      "env": {
        "HEB_DEFAULT_STORE": "590"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HEB_DEFAULT_STORE` | Default store ID | None |
| `REDIS_URL` | Redis cache URL | None (in-memory) |
| `LOG_LEVEL` | Logging level | INFO |

---

## 🎯 Usage Examples

### 🏪 Finding a Store

```
User: Find HEB stores near Austin, TX

Agent uses: store_search(address="Austin, TX", radius_miles=10)
```

### 🔍 Searching Products

```
User: Search for organic milk

Agent uses: store_change(store_id="590")
Agent uses: product_search(query="organic milk")
```

### 📋 Getting Product Details

```
User: What are the ingredients in H-E-B olive oil?

Agent uses: product_search(query="heb olive oil")
Agent uses: product_get(product_id="127074")
# Returns: ingredients, nutrition facts, warnings, dietary attributes
```

The `product_get` tool returns:
- 🥗 **Ingredients** - Full ingredient statement
- 📊 **Nutrition Facts** - Complete FDA panel
- ⚠️ **Safety Warnings** - Allergen info and precautions
- 🌿 **Dietary Attributes** - Gluten-free, organic, vegan, kosher, etc.
- 📍 **Store Location** - Aisle or section

### 🛒 Adding to Cart

```
User: Add 2 gallons of milk to my cart

Agent uses: cart_add(product_id="123456", quantity=2)
# Returns preview for confirmation

Agent uses: cart_add(product_id="123456", quantity=2, confirm=true)
# ✅ Added to cart!
```

### 🎟️ Clipping Coupons

```
User: Find coupons for cereal

Agent uses: coupon_search(query="cereal")
Agent uses: coupon_clip(coupon_id="ABC123", confirm=true)
# ✅ Coupon clipped!
```

---

## 🔐 Session Management

HEB uses bot detection that expires every ~11 minutes. This MCP handles it automatically!

### ⚡ Fast Auto-Refresh (Recommended)

With `[browser]` support installed:

```
Agent uses: session_refresh()
# ✅ Completes in ~10-15 seconds
```

### 🔑 Auto-Login

Save your credentials once for automatic login:

```
Agent uses: session_save_credentials(email="you@email.com", password="...")
# Credentials stored securely in system keyring
# Future session refreshes will auto-login!
```

---

## 🧰 Available Tools

### 🏪 Store Tools
| Tool | Description |
|------|-------------|
| `store_search` | Find stores by address |
| `store_change` | Set preferred store |
| `store_get_default` | Get current default store |

### 🔍 Product Tools
| Tool | Description |
|------|-------------|
| `product_search` | Search products with pricing |
| `product_search_batch` | Search multiple products (up to 20) |
| `product_get` | Get detailed product info |

### 🛒 Cart Tools
| Tool | Description |
|------|-------------|
| `cart_check_auth` | Check authentication status |
| `cart_get` | View cart contents |
| `cart_add` | Add item (requires confirmation) |
| `cart_add_many` | Bulk add multiple items |
| `cart_remove` | Remove item |

### 🎟️ Coupon Tools
| Tool | Description |
|------|-------------|
| `coupon_list` | List available coupons |
| `coupon_search` | Search coupons by keyword |
| `coupon_clip` | Clip a coupon |
| `coupon_clipped` | List your clipped coupons |

### 🔐 Session Tools
| Tool | Description |
|------|-------------|
| `session_status` | Check session health |
| `session_refresh` | Refresh/login session |
| `session_save_credentials` | Save credentials for auto-login |
| `session_clear` | Logout |

---

## 📚 Documentation

- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Solutions for common issues
- 🤝 [Contributing](CONTRIBUTING.md) - How to contribute
- 📝 [Changelog](CHANGELOG.md) - Version history
- 🔒 [Security](SECURITY.md) - Security policy

---

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/mgwalkerjr95/texas-grocery-mcp
cd texas-grocery-mcp

# Install with dev dependencies
pip install -e ".[dev]"
playwright install chromium

# Run tests
pytest tests/ -v

# Linting & type checking
ruff check src/
mypy src/
```

### 🐳 Docker

```bash
docker-compose up --build
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's MCP Environment                    │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │  🎭 Playwright MCP  │    │   🛒 Texas Grocery MCP      │ │
│  │  (Browser Auth)     │───▶│   (Grocery Logic)           │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
│                                        │                     │
└────────────────────────────────────────┼─────────────────────┘
                                         │
                                         ▼
                                   🌐 HEB GraphQL API
```

---

## 📄 License

MIT © Michael Walker

---

<p align="center">
  Made with ❤️ in Texas 🤠
</p>

---

## 🌐 Remote Read-Only Streamable HTTP Server

This repository also includes a separate hosted entry point for ChatGPT and other MCP clients that connect to a public Streamable HTTP MCP URL. The remote server is intentionally **read-only** and is named `texas-grocery-readonly`.

The hosted version exposes only:

- `store_search`
- `store_get_default`
- `product_search`
- `product_search_batch`
- `product_get`
- `health_live`
- `health_ready`

It intentionally omits all cart, coupon clipping, login, session, credential, browser automation, and store-changing functionality. It does **not** install Playwright or Chromium in the remote Docker image.

### Remote server warning

⚠️ This project is **not affiliated with H-E-B**. It uses unofficial H-E-B interfaces that may change, reject traffic, rate limit requests, or trigger bot-detection. Do not use the hosted read-only server for account modification, login, CAPTCHA solving, cart changes, coupon clipping, credential persistence, or browser session management.

### Local installation for HTTP hosting

```bash
git clone https://github.com/mgwalkerjr95/texas-grocery-mcp.git
cd texas-grocery-mcp
python -m venv .venv
source .venv/bin/activate
pip install .
```

No browser extras are required for the remote read-only server.

### Environment variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `PORT` | No | HTTP listen port. Defaults to `8000`. | `8000` |
| `LOG_LEVEL` | No | Logging level. | `INFO` |
| `HEB_DEFAULT_STORE` | No | Optional default H-E-B store ID used when product tools are called without `store_id`. | `590` |

Copy the example file when deploying locally or to a host:

```bash
cp .env.remote.example .env
```

### Start locally over Streamable HTTP

```bash
PORT=8000 texas-grocery-mcp-remote
```

Expected local MCP endpoint:

```text
http://localhost:8000/mcp
```

### Docker build and run

Build the read-only image with the separate remote Dockerfile:

```bash
docker build -f Dockerfile.remote -t texas-grocery-mcp-remote .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 --env-file .env.remote.example texas-grocery-mcp-remote
```

The container documents port `8000` with `EXPOSE`, but the application reads the runtime `PORT` environment variable. If your hosting provider injects a different port, pass that value through as `PORT`.

### Test with MCP Inspector

After starting the server, use an MCP Inspector or compatible MCP client and point it at:

```text
http://localhost:8000/mcp
```

Verify that the listed tools are exactly the read-only allowlist above. A harmless smoke test is to call `store_search` for a city or ZIP code, or call `product_search` with an explicit `store_id`. If H-E-B blocks or challenges traffic, keep the hosted server read-only; do not add session, browser, CAPTCHA, cart, coupon, or credential tools to bypass that failure.

### Manufact Cloud deployment

1. Push this repository to GitHub.
2. In Manufact Cloud, create a new service from the GitHub repository.
3. Select Docker-based deployment and set the Dockerfile path to `Dockerfile.remote`.
4. Configure environment variables:
   - `PORT` if Manufact does not inject one automatically.
   - `LOG_LEVEL=INFO`.
   - Optional `HEB_DEFAULT_STORE=<store id>`.
5. Do not configure H-E-B credentials, cookies, tokens, browser storage, or account secrets.
6. Deploy the service.
7. Open the service details and copy the public HTTPS base URL.
8. Append `/mcp` to obtain the public MCP endpoint.

Expected hosted endpoint format:

```text
https://<your-manufact-service-domain>/mcp
```

### Connect to ChatGPT developer mode

1. Open ChatGPT developer mode / connector configuration.
2. Add a custom MCP server.
3. Choose Streamable HTTP transport if prompted.
4. Paste the public Manufact URL ending in `/mcp`.
5. Save and test the connection.
6. Confirm ChatGPT sees only the read-only tools listed above.

The original local STDIO command remains available and unchanged:

```bash
texas-grocery-mcp
```
