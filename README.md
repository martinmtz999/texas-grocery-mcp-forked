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

## 🌐 Remote Account-Enabled Streamable HTTP Server

This repository also includes a hosted entry point for ChatGPT and other MCP clients that connect to a public Streamable HTTP MCP URL. The remote server is account-enabled and is named `texas-grocery-account`.

The hosted version exposes grocery discovery plus the requested account/session tools:

- `store_search`
- `store_get_default`
- `store_change`
- `product_search`
- `product_search_batch`
- `product_get`
- `session_status`
- `session_save_credentials`
- `session_refresh`
- `session_clear_credentials`
- `session_clear`
- `health_live`
- `health_ready`

It still intentionally omits cart and coupon tools from this connector. The remote Docker image installs browser support for session refresh/login workflows.

### Remote server warning

⚠️ This project is **not affiliated with H-E-B**. It uses unofficial H-E-B interfaces that may change, reject traffic, rate limit requests, or trigger bot-detection. Use the hosted account-enabled server only for a private deployment you control. Do not send H-E-B passwords in normal chat; use `session_save_credentials` only when the MCP client presents it as a dedicated tool call.

### Local installation for HTTP hosting

```bash
git clone https://github.com/mgwalkerjr95/texas-grocery-mcp.git
cd texas-grocery-mcp
python -m venv .venv
source .venv/bin/activate
pip install .
```

Browser support is installed in the remote Docker image for session refresh/login workflows. The Docker build explicitly installs the package browser extra and Chromium with `python -m pip install "playwright>=1.40.0"` and `python -m playwright install --with-deps chromium`.

### Environment variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `PORT` | No | HTTP listen port. Defaults to `8000`. | `8000` |
| `LOG_LEVEL` | No | Logging level. | `INFO` |
| `HEB_DEFAULT_STORE` | No | Optional default H-E-B store ID used when product tools are called without `store_id`. | `590` |
| `HEB_EMAIL` | No | Optional H-E-B account email. Configure only as a private deployment secret, never in source control. | _secret_ |
| `HEB_PASSWORD` | No | Optional H-E-B account password. Configure only as a private deployment secret, never in source control. | _secret_ |

Copy the example file when deploying locally or to a host:

```bash
cp .env.remote.example .env
```


For hosted account login without sending your password through normal chat, configure `HEB_EMAIL` and `HEB_PASSWORD` as private deployment secrets in Manufact (or your hosting provider). `session_status` will then report `credential_storage_method: "environment"`, and `session_refresh()` can attempt automatic login without requiring `session_save_credentials` in ChatGPT. If a host mounts secrets as files instead of plain environment variables, set `HEB_EMAIL_FILE` and `HEB_PASSWORD_FILE` to the mounted file paths. `session_status` also returns a non-sensitive `environment_credentials` diagnostic object showing whether the email secret, password secret, and file-style secret variables are present, without returning the secret values.

### Start locally over Streamable HTTP

```bash
PORT=8000 texas-grocery-mcp-remote
```

Expected local MCP endpoint:

```text
http://localhost:8000/mcp
```


### Lightweight store/product-only deployment

If your host's free tier cannot run Playwright/Chromium, deploy the lightweight store/product server instead. This version is intended for exact item lookup at a specific store and exposes only `store_search`, `store_get_default`, `product_search`, `product_search_batch`, `product_get`, and health checks. It does not expose session, credential, cart, coupon, or account-changing tools.

Build and run locally:

```bash
docker build -f Dockerfile.store -t texas-grocery-mcp-store .
docker run --rm -p 8000:8000 -e HEB_DEFAULT_STORE=<your-store-id> texas-grocery-mcp-store
```

For Manufact or another host, use Dockerfile path `Dockerfile.store` and set `HEB_DEFAULT_STORE` to your store ID. Then product tools can return store-specific pricing and availability without H-E-B login. You can also pass `store_id` directly to `product_search`, `product_search_batch`, and `product_get`.

### Docker build and run

Build the account-enabled remote image with the separate remote Dockerfile:

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

Verify that `session_status`, `session_save_credentials`, `session_refresh`, `session_clear_credentials`, `session_clear`, and `store_change` are present alongside the grocery discovery tools. Do not provide your H-E-B password unless the MCP client is invoking `session_save_credentials` as a dedicated tool call.

### Manufact Cloud deployment

1. Push this repository to GitHub.
2. In Manufact Cloud, create a new service from the GitHub repository.
3. Select Docker-based deployment and set the Dockerfile path to `Dockerfile.remote`.
4. Configure environment variables:
   - `PORT` if Manufact does not inject one automatically.
   - `LOG_LEVEL=INFO`.
   - Optional `HEB_DEFAULT_STORE=<store id>`.
5. Do not put H-E-B credentials, cookies, tokens, browser storage, or account secrets in source control or deployment logs. Add credentials only through the `session_save_credentials` MCP tool when needed.
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
6. Confirm ChatGPT sees `session_status`, `session_save_credentials`, `session_refresh`, `session_clear_credentials`, `session_clear`, and `store_change`.

The original local STDIO command remains available and unchanged:

```bash
texas-grocery-mcp
```
