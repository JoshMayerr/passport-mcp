import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx


@dataclass
class PathData:
    """Structured container for path-specific data."""

    headers: Dict[str, str]
    cookies: Dict[str, str]
    first_seen: str
    last_updated: str
    request_count: int


@dataclass
class DomainData:
    """Structured container for domain-specific data with path inheritance."""

    paths: Dict[str, PathData]  # Key is the path, e.g. "/", "/api", "/api/v2"
    first_seen: str
    last_updated: str
    request_count: int

    def get_credentials_for_path(self, path: str) -> tuple[Dict[str, str], Dict[str, str]]:
        """Get merged headers and cookies for a specific path, applying inheritance.

        Args:
            path: The path to get credentials for (e.g. "/api/v2/users")

        Returns:
            Tuple of (headers, cookies) with inheritance applied
        """
        # Split path into components
        path_parts = path.split("/")
        current_path = ""
        merged_headers: Dict[str, str] = {}
        merged_cookies: Dict[str, str] = {}

        # Walk up the path tree
        for i in range(len(path_parts)):
            current_path = "/" + "/".join(filter(None, path_parts[:i + 1]))
            if current_path in self.paths:
                path_data = self.paths[current_path]
                # Update with more specific path data
                merged_headers.update(path_data.headers)
                merged_cookies.update(path_data.cookies)

        return merged_headers, merged_cookies


class BrowserPassportError(Exception):
    """Base exception for BrowserPassport errors."""

    pass


class StorageError(BrowserPassportError):
    """Raised when there are issues with the storage system."""

    pass


class AuthenticationError(BrowserPassportError):
    """Raised when request fails due to authentication issues."""

    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        domain = urlparse(url).netloc.removeprefix("www.")
        self.message = (
            f"Authentication failed for {domain} (status {status_code}). "
            "Please use the Chrome extension to save new credentials for this site."
        )
        super().__init__(self.message)


class BrowserPassport:
    """Enhanced HTTP client that uses stored browser credentials."""

    DEFAULT_STORAGE_PATH = "~/Library/Logs/request_monitor/domains.json"
    # EXCLUDED_HEADERS = {"accept", "content-type", "content-encoding", "content-length"}
    EXCLUDED_HEADERS = {}

    def __init__(
        self,
        storage_path: Optional[str] = None,
        timeout: float = 30.0,
        verify: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize BrowserPassport client.

        Args:
            storage_path: Path to credentials storage. Defaults to standard location.
            timeout: Request timeout in seconds.
            verify: Whether to verify SSL certificates.
            logger: Optional logger instance.
        """
        self.storage_path = os.path.expanduser(
            storage_path or self.DEFAULT_STORAGE_PATH)
        self.logger = logger or logging.getLogger(__name__)
        self.client = httpx.Client(timeout=timeout, verify=verify)

        # Validate storage on initialization
        if not self._validate_storage():
            raise StorageError(
                "Storage not found or invalid. Please run the Chrome extension first."
            )

    def _validate_storage(self) -> bool:
        """Check if storage exists and is valid JSON."""
        try:
            storage_path = Path(self.storage_path)
            if not storage_path.exists():
                self.logger.warning(
                    "Storage file not found at %s", self.storage_path)
                return False

            with open(storage_path) as f:
                json.load(f)  # Validate JSON
            return True

        except (json.JSONDecodeError, PermissionError) as e:
            self.logger.error("Storage validation failed: %s", str(e))
            return False

    def _load_domain_data(self, url: str) -> Optional[DomainData]:
        """Load and validate domain data for a URL."""
        try:
            domain = urlparse(url).netloc.removeprefix("www.")

            with open(self.storage_path) as f:
                storage = json.load(f)

            if domain not in storage:
                return None

            data = storage[domain]

            # Convert stored paths to PathData objects
            paths = {}
            for path, path_data in data.get("paths", {}).items():
                paths[path] = PathData(
                    headers=path_data.get("headers", {}),
                    cookies=path_data.get("cookies", {}),
                    first_seen=path_data.get("first_seen", ""),
                    last_updated=path_data.get("last_updated", ""),
                    request_count=path_data.get("request_count", 0)
                )

            return DomainData(
                paths=paths,
                first_seen=data.get("first_seen", ""),
                last_updated=data.get("last_updated", ""),
                request_count=data.get("request_count", 0)
            )

        except Exception as e:
            self.logger.error("Error loading domain data: %s", str(e))
            return None

    def _get_storage(self) -> Dict[str, Any]:
        """Get the storage data."""
        with open(self.storage_path) as f:
            return json.load(f)

    def _prepare_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare request with stored credentials."""
        request_kwargs = kwargs.copy()

        # If headers or cookies are provided, use them directly
        if headers is not None:
            request_kwargs["headers"] = headers
        if cookies is not None:
            request_kwargs["cookies"] = cookies

        # Only use stored credentials if no headers/cookies provided
        if headers is None or cookies is None:
            domain_data = self._load_domain_data(url)
            if domain_data:
                # Get path from URL
                path = urlparse(url).path or "/"

                # Get credentials with inheritance
                stored_headers, stored_cookies = domain_data.get_credentials_for_path(
                    path)

                if headers is None:
                    # Merge headers, prioritizing user-provided ones
                    merged_headers = {**stored_headers, **(headers or {})}
                    # Remove excluded headers
                    request_kwargs["headers"] = {
                        k: v for k, v in merged_headers.items() if k.lower() not in self.EXCLUDED_HEADERS
                    }

                if cookies is None:
                    # Merge cookies, prioritizing user-provided ones
                    request_kwargs["cookies"] = {
                        **stored_cookies, **(cookies or {})}

        return request_kwargs

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make an HTTP request with stored credentials.

        Args:
            method: HTTP method to use
            url: Target URL
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            AuthenticationError: If authentication fails
            StorageError: If there are storage-related issues
            httpx.RequestError: For other request errors
        """
        request_kwargs = self._prepare_request(method, url, **kwargs)
        response = self.client.request(method, url, **request_kwargs)

        if response.status_code in (401, 403):
            raise AuthenticationError(url, response.status_code)

        return response

    def get(self, url: str, **kwargs) -> httpx.Response:
        """Send a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        """Send a POST request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        """Send a PUT request."""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        """Send a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def list_domains(self) -> List[str]:
        """List all domains with stored credentials."""
        try:
            storage = self._get_storage()
            return sorted(storage.keys())
        except Exception as e:
            raise StorageError(f"Failed to list domains: {str(e)}") from e

    def get_domain_stats(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific domain."""
        try:
            storage = self._get_storage()
            if domain not in storage:
                return None
            return {
                "count": len(storage[domain]),
                "last_updated": max(x.timestamp for x in storage[domain]),
            }
        except Exception as e:
            raise StorageError(f"Failed to get domain stats: {str(e)}") from e
