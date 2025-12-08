"""Global fixtures for Meteocat tests."""
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_client_session():
    """Mock aiohttp client session to avoid lingering timers and real network calls."""
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession", return_value=MagicMock()) as mock_session:
        yield mock_session

@pytest.fixture(autouse=True)
def mock_get_clientsession_custom():
    """Mock the custom component's import of async_get_clientsession."""
    # We need to patch it where it's imported in the custom component
    with patch("custom_components.meteocat_community_edition.coordinator.async_get_clientsession", return_value=MagicMock()), \
         patch("custom_components.meteocat_community_edition.config_flow.async_get_clientsession", return_value=MagicMock()):
        yield
