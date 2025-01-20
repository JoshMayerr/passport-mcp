import pytest
import json
from pathlib import Path
from browserpassport.client import AuthenticationError, BrowserPassport


@pytest.fixture
def mock_storage(tmp_path):
    """Create a mock storage file with test credentials"""
    storage_path = tmp_path / "domains.json"
    storage_data = {
        "example.com": {
            "headers": {
                "authorization": "Bearer test-token"
            },
            "cookies": {
                "session": "test-session"
            }
        }
    }
    storage_path.write_text(json.dumps(storage_data))
    return storage_path


def test_client_initialization(mock_storage):
    client = BrowserPassport(storage_path=str(mock_storage))
    assert client is not None
