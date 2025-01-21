# PassportMCP Python SDK

PassportMCP (ppmcp) lets you build MCP servers for any given website with automatic browser auth syncing. Every website is fair game. It wraps FastMCP and automatically adds necessary auth headers and cookies from the browser to outbound requests. As long as you log in through the browser, it's ready to be used. Often easier than paying for developer APIs (ex: twitter/X), avoiding rate limits, waiting for approval, or great for sites that don't have one.

## Features

- Automatic browser auth syncing (for any auth type)
- Normal MCP tool creation
- Works with any website
- Always uses latest auth state
- All credentials stay on your machine

## Quick Start

1. **Install the Package**

```bash
pip install ppmcp
```

2. **Set Up Native Messaging and Auth Syncing**

```bash
ppmcp setup  # Sets up with Chrome Web Store extension
```

3. **Enable Request Monitoring**

   - Click the PassportMCP extension icon in Chrome
   - Toggle "Monitor Requests" on
   - Visit and log into your target website

4. **Create Your First MCP Tool**

```python
from passportmcp import PassportMCP

# Create an MCP instance
mcp = PassportMCP("example", "example.com")

# Define a tool
@mcp.tool()
async def get_data():
    response = mcp.client.get("https://example.com/api/data")
    return response.json()
```

## Installation Options

### Option 1: Chrome Web Store Extension (Recommended)

```bash
pip install ppmcp
ppmcp setup
```

### Option 2: Local Development

1. **Build the Extension**

```bash
git clone https://github.com/joshmayerr/passport-mcp.git
cd extension
npm install
npm run build  # or npm run dev for watch mode
```

2. **Load in Chrome**

   - Open Chrome and go to `chrome://extensions`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `extension/dist` directory
   - Note the extension ID from Chrome (shown under the extension name)

3. **Set Up Native Messaging**

```bash
ppmcp setup --local --extension-id=your_extension_id
# OR
ppmcp setup --local  # You'll be prompted for the ID
```

### CLI Commands

- `ppmcp setup` - Set up native messaging
- `ppmcp doctor` - Check installation status
- `ppmcp uninstall` - Remove PassportMCP

## How It Works

PassportMCP consists of three main components:

1. **Chrome Extension**

   - Monitors web requests
   - Captures authentication state
   - Sends to native host

2. **Native Host**

   - Receives data from extension
   - Stores authentication state
   - Provides data to SDK

3. **SDK**
   - PassportMCP: High-level MCP tool creation
   - BrowserPassport: Low-level auth handling

## Advanced Example: LinkedIn API

```python
from passportmcp import PassportMCP

mcp = PassportMCP("linkedin", "linkedin.com")

@mcp.tool()
async def search_linkedin(query: str):
    response = mcp.client.get(
        "https://www.linkedin.com/voyager/api/graphql",
        params={
            "includeWebMetadata": "true",
            "variables": "()",
            "queryId": "voyagerDashMySettings.7ea6de345b41dfb57b660a9a4bebe1b8"
        }
    )
    return response.json()
```

## Security

- ✅ Credentials never leave your machine
- ✅ No cloud storage or transmission
- ✅ Limited to authorized domains
- ✅ LLMs never see your credentials

Unlike services like Anon and Rabbit that automate accounts in the cloud, PassportMCP keeps everything local.

## Development

For SDK development:

```bash
cd sdks/python
pip install -e .
```

## Roadmap

- [ ] TypeScript SDK
- [ ] Firefox extension
- [ ] Safari extension
- [ ] Auth state sharing
- [ ] Enterprise features
- [ ] More language SDKs

## License

MIT License - see [LICENSE](LICENSE) for details
