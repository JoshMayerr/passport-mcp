# Browser Passport Extension

A browser extension for managing web identities.

## Development

1. Install dependencies:

```bash
npm install
```

2. Build the extension:

```bash
npm run build
```

For development with hot reload:

```bash
npm run dev
```

3. Load the extension:

- Open Chrome/Edge
- Go to `chrome://extensions`
- Enable "Developer mode"
- Click "Load unpacked"
- Select the `dist` directory

## Structure

- `src/background/`: Background service worker
- `src/popup/`: Extension popup UI
- `src/types/`: Shared TypeScript types
- `manifest.json`: Extension manifest
- `webpack.config.js`: Build configuration
- `tsconfig.json`: TypeScript configuration

## Package for Web Store

```bash
npm run build
npm run package
```

This creates an `extension.zip` folder that is ready to be uploaded.
