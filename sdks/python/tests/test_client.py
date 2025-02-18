import json
import pytest


@pytest.fixture
def mock_storage(tmp_path):
    """Create a mock storage file with test credentials"""
    storage_path = tmp_path / "domains.json"
    storage_data = {
        "example.com": {
            "headers": {"authorization": "Bearer test-token"},
            "cookies": {"session": "test-session"},
        }
    }
    storage_path.write_text(json.dumps(storage_data))
    return storage_path


# def test_client_basic_flow():
# client = BrowserPassport()
# Add basic flow test here based on your implementation
# For example:
# result = client.authenticate()
# assert result.success is True
