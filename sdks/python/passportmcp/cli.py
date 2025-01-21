import json
import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional

import click


class PlatformPaths(NamedTuple):
    """Platform-specific paths for BrowserPassport installation"""

    native_host_dir: Path
    chrome_manifest_dir: Path
    data_dir: Path
    log_dir: Path


class SetupManager:
    """Manages BrowserPassport setup and installation"""

    NATIVE_HOST_NAME = "com.browserpassport.native_messaging_host"
    # We'll replace this with actual ID after Chrome Web Store publication
    CHROME_STORE_ID = "alkipahekcclcplmedmifnbeonknmhoh"

    def __init__(self, extension_id: Optional[str] = None):
        self.paths = self._get_platform_paths()
        self.extension_id = extension_id or self.CHROME_STORE_ID

    @staticmethod
    def _get_platform_paths() -> PlatformPaths:
        """Get platform-specific paths based on OS"""
        system = platform.system()

        if system == "Darwin":  # macOS
            return PlatformPaths(
                native_host_dir=Path.home() / "Library/Application Support/BrowserPassport",
                chrome_manifest_dir=Path.home()
                / "Library/Application Support/Google/Chrome/NativeMessagingHosts",
                data_dir=Path.home() / "Library/Logs/request_monitor",
                log_dir=Path.home() / "Library/Logs/BrowserPassport",
            )
        elif system == "Linux":
            return PlatformPaths(
                native_host_dir=Path.home() / ".local/share/browserpassport",
                chrome_manifest_dir=Path.home() / ".config/google-chrome/NativeMessagingHosts",
                data_dir=Path.home() / ".local/share/browserpassport/data",
                log_dir=Path.home() / ".local/share/browserpassport/logs",
            )
        elif system == "Windows":
            raise NotImplementedError("Windows support coming soon!")
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def create_directories(self) -> None:
        """Create necessary directories for installation"""
        for directory in self.paths:
            directory.mkdir(parents=True, exist_ok=True)

    def install_native_host(self, shared_dir: Path) -> Path:
        """Install native messaging host from shared directory"""
        source_path = shared_dir / "native_host.py"
        if not source_path.exists():
            raise FileNotFoundError(f"Native host not found at {source_path}")

        native_host_path = self.paths.native_host_dir / "native_host.py"
        shutil.copy2(source_path, native_host_path)

        # Make executable
        current = stat.S_IMODE(os.lstat(native_host_path).st_mode)
        os.chmod(native_host_path, current | stat.S_IXUSR |
                 stat.S_IXGRP | stat.S_IXOTH)

        return native_host_path

    def create_manifest(self, native_host_path: Path) -> Path:
        """Create Chrome native messaging host manifest"""
        manifest_path = self.paths.chrome_manifest_dir / \
            f"{self.NATIVE_HOST_NAME}.json"

        manifest = {
            "name": self.NATIVE_HOST_NAME,
            "description": "BrowserPassport Native Messaging Host",
            "path": str(native_host_path),
            "type": "stdio",
            "allowed_origins": [f"chrome-extension://{self.extension_id}/"],
        }

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def test_native_host(self, native_host_path: Path) -> bool:
        """Test native messaging host functionality"""
        try:
            result = subprocess.run(
                [str(native_host_path)], input=b'{"type": "test"}\n', capture_output=True, timeout=2
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            # Timeout is expected as the host keeps running
            return True

    def check_installation(self) -> List[str]:
        """Check installation and return list of issues"""
        issues = []

        # Check directories
        for directory in self.paths:
            if not directory.exists():
                issues.append(f"Missing directory: {directory}")

        # Check native host
        native_host_path = self.paths.native_host_dir / "native_host.py"
        if not native_host_path.exists():
            issues.append("Native host not installed")
        elif not os.access(native_host_path, os.X_OK):
            issues.append("Native host not executable")

        # Check manifest
        manifest_path = self.paths.chrome_manifest_dir / \
            f"{self.NATIVE_HOST_NAME}.json"
        if not manifest_path.exists():
            issues.append("Chrome manifest missing")
        else:
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                if manifest.get("path") != str(native_host_path):
                    issues.append(
                        "Manifest points to wrong native host location")
            except json.JSONDecodeError:
                issues.append("Invalid manifest JSON")

        return issues


@click.group()
def cli():
    """BrowserPassport command line interface"""
    pass


@cli.command()
@click.option('--local', is_flag=True, help='Use local extension instead of Chrome Web Store version')
@click.option('--extension-id', help='Extension ID for local extension')
def setup(local: bool, extension_id: Optional[str]):
    """Set up BrowserPassport"""
    click.echo("🚀 Setting up BrowserPassport...")

    if local and not extension_id:
        extension_id = click.prompt('Please enter your local extension ID')

    try:
        manager = SetupManager(extension_id if local else None)

        # Create directories
        click.echo("\n📁 Creating directories...")
        manager.create_directories()

        # Install native host from shared directory
        click.echo("\n📦 Installing native messaging host...")
        shared_dir = Path(__file__).parent.parent.parent.parent / \
            "shared" / "native-host"
        if not (shared_dir / "native_host.py").exists():
            raise RuntimeError("Native host not found in shared directory")
        native_host_path = manager.install_native_host(shared_dir)
        click.echo(f"Installed to {native_host_path}")

        # Create manifest
        click.echo("\n📝 Creating Chrome manifest...")
        manifest_path = manager.create_manifest(native_host_path)
        click.echo(f"Created manifest at {manifest_path}")

        # Test installation
        click.echo("\n🔍 Testing native messaging host...")
        if manager.test_native_host(native_host_path):
            click.echo("✓ Native host test successful")
        else:
            click.echo("⚠️ Native host test failed")

        if not local:
            # Install extension from Chrome Web Store
            store_url = (
                f"https://chrome.google.com/webstore/detail/browserpassport/{manager.CHROME_STORE_ID}"
            )
            click.echo(f"\n🔗 Installing Chrome extension from: {store_url}")
            click.launch(store_url)
        else:
            # Instructions for local extension
            click.echo("\n🔧 Using local extension")
            click.echo("To complete setup:")
            click.echo("1. Open Chrome and go to chrome://extensions")
            click.echo("2. Enable 'Developer mode'")
            click.echo("3. Click 'Load unpacked'")
            click.echo(
                "4. Select the 'extension/dist' directory from your local repository")

        click.confirm(
            "\nPress Enter after installing the extension", default=True)

        click.echo("\n✨ Setup complete!")
        click.echo("\nExample usage:")
        click.echo("""
    from browserpassport import BrowserPassport

    client = BrowserPassport()
    response = client.get('https://example.com/api/data')
    print(response.json())
        """)

        click.echo("\nTo check installation status:")
        click.echo("    ppmcp doctor")

    except Exception as e:
        click.echo(f"\n❌ Setup failed: {str(e)}")
        click.echo("\nTry running 'ppmcp doctor' to diagnose the issue")
        sys.exit(1)


@cli.command()
def doctor():
    """Check BrowserPassport installation"""
    click.echo("🏥 Running diagnostics...")

    try:
        manager = SetupManager()
        issues = manager.check_installation()

        if not issues:
            click.echo("\n✨ All checks passed!")
        else:
            click.echo("\n⚠️ Found issues:")
            for issue in issues:
                click.echo(f"  • {issue}")

            click.echo(
                "\nTry running 'ppmcp setup' to fix these issues")
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Diagnostics failed: {str(e)}")
        sys.exit(1)


@cli.command()
def uninstall():
    """Remove BrowserPassport installation"""
    if not click.confirm("⚠️ This will remove all BrowserPassport files. Continue?"):
        return

    try:
        manager = SetupManager()

        click.echo("\n🗑 Removing files...")

        # Remove native host
        native_host_path = manager.paths.native_host_dir / "native_host.py"
        if native_host_path.exists():
            native_host_path.unlink()
            click.echo(f"Removed {native_host_path}")

        # Remove manifest
        manifest_path = manager.paths.chrome_manifest_dir / \
            f"{manager.NATIVE_HOST_NAME}.json"
        if manifest_path.exists():
            manifest_path.unlink()
            click.echo(f"Removed {manifest_path}")

        # Remove data directory
        if manager.paths.data_dir.exists():
            shutil.rmtree(manager.paths.data_dir)
            click.echo(f"Removed {manager.paths.data_dir}")

        click.echo("\n✨ Uninstall complete!")

    except Exception as e:
        click.echo(f"\n❌ Uninstall failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
