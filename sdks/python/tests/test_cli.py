import json
from pathlib import Path

from passportmcp.cli import SetupManager


def test_setup_manager_paths():
    manager = SetupManager()
    assert all(isinstance(p, Path) for p in manager.paths)


def test_create_manifest(tmp_path):
    manager = SetupManager()
    native_host_path = tmp_path / "native_host.py"
    native_host_path.touch()

    # Override chrome manifest dir for testing
    manager.paths = manager.paths._replace(chrome_manifest_dir=tmp_path)

    manifest_path = manager.create_manifest(native_host_path)
    assert manifest_path.exists()

    # Verify manifest contents
    manifest_data = json.loads(manifest_path.read_text())
    assert manifest_data["name"] == manager.NATIVE_HOST_NAME
    assert manifest_data["path"] == str(native_host_path)
