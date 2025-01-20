from functools import wraps
from typing import Any, Callable, Optional

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
        self.browser = BrowserPassport(**kwargs)
        self._tools = {}

    def tool(self, name: Optional[str] = None) -> Callable:
        """Decorator to register an MCP tool function.
        The decorated function will automatically have browser authentication injected.

        Args:
            name: Optional name for the tool. Defaults to the function name.
        """

        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__

            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Here we would inject the authenticated browser instance
                # and any other MCP-specific functionality
                return await func(*args, **kwargs)

            # Store metadata about the tool
            wrapper._is_tool = True
            wrapper._tool_name = tool_name
            self._tools[tool_name] = wrapper

            return wrapper

        return decorator

    def get_tools(self) -> dict:
        """Get all registered tools."""
        return self._tools

    def __getattr__(self, name: str) -> Any:
        """Proxy unknown attributes to the browser instance."""
        return getattr(self.browser, name)
