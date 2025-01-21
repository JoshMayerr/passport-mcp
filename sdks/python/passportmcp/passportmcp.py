from typing import Any

from .client import BrowserPassport


class PassportMCP:
    """A wrapper around BrowserPassport that provides MCP (Multi-Client Protocol) functionality.
    This allows developers to easily build MCP servers for any website by automatically syncing
    browser authentication to outbound requests."""

    def __init__(self, name: str, domain: str, **kwargs):
        """Initialize PassportMCP.

        Args:
            name: The name of the MCP service (e.g. 'linkedin')
            domain: The domain to authenticate against (e.g. 'linkedin.com')
            **kwargs: Additional arguments passed to BrowserPassport
        """
        self.name = name
        self.domain = domain
        self.client = BrowserPassport(**kwargs)

    def __getattr__(self, name: str) -> Any:
        """Proxy unknown attributes to the browser instance."""
        return getattr(self.client, name)
