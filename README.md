# PassportMCP

PassportMCP lets you build MCP servers for any given website with automatic browser auth syncing. It wraps FastMCP and automatically adds necessary auth headers and cookies from the browser to outbound requests. Bulid any MCP you want without worrying about auth! As long as you log in through the browser, it's fair game. Often easier than paying for developer APIs (ex: twitter/X), avoiding rate limits, or great for sites that don't have one.

## How It Works

1. Install the Chrome extension
2. Log into your website normally in Chrome
3. The extension sync authentication headers and cookies
4. Use PassportMCP to build authenticated MCP tools

```python
from passportmcp import PassportMCP

# Create an MCP instance for LinkedIn
mcp = PassportMCP("linkedin", "linkedin.com")

# Define MCP tools using the decorator
@mcp.tool()
async def search_linkedin(query: str):
    # make a get request to the real linkedin api, not the developer api
    response = mcp.browser.get(
        "https://www.linkedin.com/voyager/api/search/blended",
        params={"keywords": query}
    )
    return response.json()
```

## Features

- Automatic browser auth syncing
- Normal MCP tool creation
- Works with any website
- Always uses latest auth state
- Handles cookies and headers

## Installation (order doesn't matter)

1. **Install Chrome Extension**:

   - Visit [Chrome Web Store](#) and install PassportMCP extension

2. **Install Python SDK**:
   ```bash
   pip install passportmcp
   passportmcp setup  # Sets up native messaging
   ```

## Quick Start

1. **Enable Monitoring**:

   - Click the PassportMCP icon in Chrome
   - Toggle "Monitor Requests" on
   - Visit and log into your target website

2. **Create MCP Tools**:

   ```python
   from passportmcp import PassportMCP

   # Create MCP instance
   mcp = PassportMCP("linkedin", "linkedin.com")

   # Define tools
   @mcp.tool()
   async def get_profile(profile_id: str):
       response = mcp.browser.get(
           f"https://www.linkedin.com/voyager/api/profiles/{profile_id}"
       )
       return response.json()
   ```

3. Use the MCP server with a client as normal.

## Architecture

PassportMCP consists of three main components:

1. **Chrome Extension**:

   - Monitors web requests
   - Captures authentication state
   - Sends to native host

2. **Native Host**:

   - Receives data from extension
   - Stores authentication state
   - Provides data to SDK

3. **SDK**:
   - PassportMCP: High-level MCP tool creation
   - BrowserPassport: Low-level auth handling

## Development Setup

1. **Clone Repository**:

   ```bash
   git clone https://github.com/joshmayerr/passport-mcp.git
   cd passport-mcp
   ```

2. **Extension Development**:

   ```bash
   cd extension
   npm install
   npm run dev           # Watch mode
   ```

   Then load `extension/dist` in Chrome as an unpacked extension

3. **Python SDK Development**:
   ```bash
   cd sdks/python
   pip install -e .
   ```

## Project Structure

```
passport-mcp/
├── extension/            # Chrome extension
├── sdks/
│   ├── python/          # Python SDK
│   └── typescript/      # TypeScript SDK (coming soon)
└── shared/
    └── native-host/     # Native messaging host
```

## Security

- Only captures auth-related data
- Stores securely on local machine
- No remote data transmission
- Limited to authorized domains

All credentials NEVER leave your computer, unlike startups like Anon and Rabbit who want to automate your accounts in the cloud. The LLM will never see your credentials either.

## Roadmap

- [ ] TypeScript SDK
- [ ] Firefox extension
- [ ] Safari extension
- [ ] Auth state sharing
- [ ] Enterprise features
- [ ] More language SDKs

## FAQ

**Q: How does it capture auth?**
A: The extension monitors web requests and captures auth-related headers and cookies.

**Q: Is it secure?**
A: Yes! All data stays on your machine and is only used for domains you authorize.

**Q: What browsers are supported?**
A: Currently Chrome only.

## License

MIT License - see [LICENSE](LICENSE) for details
