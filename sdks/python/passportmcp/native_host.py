#!/usr/bin/env python3
import sys
import json
import struct
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def get_data_dir() -> Path:
    """Get platform-specific data directory."""
    system = sys.platform
    if system == "darwin":  # macOS
        return Path.home() / "Library/Logs/request_monitor"
    elif system == "linux":
        return Path.home() / ".local/share/browserpassport/data"
    elif system == "win32":
        return Path.home() / "AppData/Local/BrowserPassport/Data"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_log_dir() -> Path:
    """Get platform-specific log directory."""
    system = sys.platform
    if system == "darwin":  # macOS
        return Path.home() / "Library/Logs/BrowserPassport"
    elif system == "linux":
        return Path.home() / ".local/share/browserpassport/logs"
    elif system == "win32":
        return Path.home() / "AppData/Local/BrowserPassport/Logs"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def ensure_dir(path: Path) -> None:
    """Ensure directory exists with correct permissions."""
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":  # Skip on Windows
        path.chmod(0o755)  # rwxr-xr-x


def log(message: str) -> None:
    """Log message with timestamp."""
    try:
        log_dir = get_log_dir()
        ensure_dir(log_dir)
        log_path = log_dir / "native_host.log"

        timestamp = datetime.now().isoformat()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {os.getpid()} - {message}\n")
    except Exception as e:
        # If logging fails, write to stderr as last resort
        print(f"Logging failed: {e}", file=sys.stderr)


def send_message(message: Dict[str, Any]) -> None:
    """Send message to Chrome extension."""
    try:
        encoded_message = json.dumps(message).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("@I", len(encoded_message)))
        sys.stdout.buffer.write(encoded_message)
        sys.stdout.buffer.flush()
    except Exception as e:
        log(f"Error sending message: {e}")
        raise


def read_message() -> Optional[Dict[str, Any]]:
    """Read message from Chrome extension."""
    try:
        # Read message length (first 4 bytes)
        text_length_bytes = sys.stdin.buffer.read(4)
        if not text_length_bytes:
            return None  # EOF reached

        text_length = struct.unpack("@I", text_length_bytes)[0]

        # Read the message of specified length
        message_bytes = sys.stdin.buffer.read(text_length)
        message = json.loads(message_bytes.decode("utf-8"))
        return message

    except Exception as e:
        log(f"Error reading message: {e}")
        raise


class DomainStorage:
    """Manages domain-specific credential storage."""

    def __init__(self):
        self.data_dir = get_data_dir()
        ensure_dir(self.data_dir)
        self.storage_path = self.data_dir / "domains.json"
        self.domains = self.load_storage()

    def load_storage(self) -> Dict[str, Any]:
        """Load domain storage from disk."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log(f"Error loading storage: {e}")
            return {}

    def save_storage(self) -> None:
        """Save domain storage to disk."""
        try:
            # Create atomic backup first
            if self.storage_path.exists():
                backup_path = self.storage_path.with_suffix(".json.bak")
                self.storage_path.replace(backup_path)

            # Write new data
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.domains, f, indent=2, sort_keys=True)

        except Exception as e:
            log(f"Error saving storage: {e}")
            raise

    def update_domain(
        self, domain: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update stored data for a domain."""
        timestamp = request_data["timestamp"]

        if domain not in self.domains:
            self.domains[domain] = {
                "first_seen": timestamp,
                "last_updated": timestamp,
                "request_count": 0,
                "headers": {},
                "cookies": {},
            }

        domain_data = self.domains[domain]
        domain_data["last_updated"] = timestamp
        domain_data["request_count"] += 1

        # Update headers with latest value
        for header in request_data["headers"]:
            name = header["name"].lower()  # Normalize header names
            # Skip certain headers that shouldn't be stored
            if name not in {"content-length", "content-encoding", "host"}:
                domain_data["headers"][name] = header["value"]

        # Update cookies with latest value
        for cookie in request_data["cookies"]:
            domain_data["cookies"][cookie["name"]] = cookie["value"]

        self.save_storage()
        return domain_data


def handle_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle request data from Chrome extension."""
    try:
        # Extract and normalize domain
        domain = data["url"].split("/")[2].removeprefix("www.")

        # Initialize storage and update domain data
        storage = DomainStorage()
        updated_data = storage.update_domain(domain, data)

        return {
            "status": "success",
            "message": "Domain data updated successfully",
            "domain": domain,
            "request_count": updated_data["request_count"],
        }

    except Exception as e:
        log(f"Error handling request data: {e}")
        return {"status": "error", "message": f"Error processing request: {str(e)}"}


def main() -> None:
    """Main entry point."""
    log("Native host started")

    while True:
        try:
            message = read_message()
            if message is None:  # EOF reached
                log("Input stream closed, exiting")
                break

            log(f"Received message type: {message.get('type', 'unknown')}")

            if message.get("type") == "request_data":
                response = handle_request_data(message["data"])
            else:
                response = {
                    "status": "error",
                    "message": f"Unknown message type: {message.get('type')}",
                }

            log(f"Sending response: {response}")
            send_message(response)

        except Exception as e:
            log(f"Fatal error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
