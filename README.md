# PassportMCP

PassportMCP is a powerful tool that lets developers build MCP (Multi-Client Protocol) servers for any website by automatically syncing browser authentication to outbound requests. It's built on top of BrowserPassport, which handles the low-level browser authentication state capture and reuse.

## How It Works

1. Install the Chrome extension
2. Log into your website normally in Chrome
3. The extension captures authentication headers and cookies
4. Use PassportMCP to build authenticated MCP tools

```python
from passportmcp import PassportMCP

# Create an MCP instance for LinkedIn
mcp = PassportMCP("linkedin", "linkedin.com")

# Define MCP tools using the decorator
@mcp.tool()
async def search_linkedin(query: str):
    response = mcp.browser.get(
        "https://www.linkedin.com/voyager/api/search/blended",
        params={"keywords": query}
    )
    return response.json()
```

## Features

- 🔒 Automatic browser auth syncing
- 🚀 Simple MCP tool creation
- 🛠️ Works with any website
- 🔄 Always uses latest auth state
- 📋 Handles cookies and headers
- ⚡ Zero configuration needed

## Installation

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
   git clone https://github.com/your-org/passport-mcp.git
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

PassportMCP prioritizes security:

- Only captures auth-related data
- Stores securely on local machine
- No remote data transmission
- Limited to authorized domains

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. **Fork and Clone**:

   ```bash
   git clone https://github.com/your-username/passport-mcp.git
   ```

2. **Make Changes**:
   - Create feature branch
   - Make changes
   - Add tests
   - Submit PR

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
A: Currently Chrome only. Firefox and Safari coming soon.

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

- 📚 [Documentation](https://docs.passportmcp.dev)
- 💬 [Discord Community](https://discord.gg/passportmcp)
- 🐛 [Issue Tracker](https://github.com/your-org/passport-mcp/issues)
- 📧 Email: support@passportmcp.dev
