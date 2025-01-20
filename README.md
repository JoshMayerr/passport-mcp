# BrowserPassport

BrowserPassport lets you make authenticated requests to websites from your local applications by capturing and reusing your browser's authentication state.

## How It Works

1. Install the Chrome extension
2. Log into your website normally in Chrome
3. The extension captures authentication headers and cookies
4. Use our SDK to make authenticated requests from your code

```python
from browserpassport import BrowserPassport

client = BrowserPassport()
response = client.get('https://example.com/api/data')  # Automatically includes auth!
```

## Features

- 🔒 Capture authentication state from Chrome
- 🚀 Use in any local application
- 🛠️ Simple SDK interface
- 🔄 Always uses latest auth state
- 📋 Works with cookies and headers
- ⚡ Zero configuration needed

## Installation

1. **Install Chrome Extension**:

   - Visit [Chrome Web Store](#) and install BrowserPassport

2. **Install Python SDK**:
   ```bash
   pip install browserpassport
   browserpassport setup  # Sets up native messaging
   ```

## Quick Start

1. **Enable Monitoring**:

   - Click the BrowserPassport icon in Chrome
   - Toggle "Monitor Requests" on
   - Visit and log into your website

2. **Use in Code**:

   ```python
   from browserpassport import BrowserPassport

   # Create client
   client = BrowserPassport()

   # Make authenticated requests
   response = client.get('https://example.com/api/data')
   print(response.json())

   # POST requests work too
   response = client.post('https://example.com/api/update', json={'key': 'value'})
   ```

## How It Works

BrowserPassport has three main components:

1. **Chrome Extension**:

   - Monitors web requests
   - Captures authentication headers and cookies
   - Sends to native host

2. **Native Host**:

   - Receives data from extension
   - Stores authentication state
   - Provides data to SDK

3. **SDK**:
   - Reads stored authentication
   - Adds to outgoing requests
   - Handles errors gracefully

## Development Setup

1. **Clone Repository**:

   ```bash
   git clone https://github.com/your-org/browserpassport.git
   cd browserpassport
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
browserpassport/
├── extension/            # Chrome extension
├── sdks/
│   ├── python/          # Python SDK
│   └── typescript/      # TypeScript SDK (coming soon)
└── shared/
    └── native-host/     # Native messaging host
```

## Authentication Support

BrowserPassport captures all forms of browser authentication:

- Cookies (session, persistent)
- Authorization headers
- Custom auth headers
- API keys in headers
- CSRF tokens

## Security

BrowserPassport prioritizes security:

- Only captures auth-related data
- Stores securely on local machine
- No remote data transmission
- Limited to authorized domains

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. **Fork and Clone**:

   ```bash
   git clone https://github.com/your-username/browserpassport.git
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

- 📚 [Documentation](https://docs.browserpassport.dev)
- 💬 [Discord Community](https://discord.gg/browserpassport)
- 🐛 [Issue Tracker](https://github.com/your-org/browserpassport/issues)
- 📧 Email: support@browserpassport.dev
