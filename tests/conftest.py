"""Global fixtures for Meteocat tests."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        from pytest_socket import enable_socket
        enable_socket()
    except ImportError:
        pass
    
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def pytest_configure(config):
    """Enable socket for Windows tests globally."""
    # This is a hack to bypass pytest-socket on Windows where ProactorEventLoop needs it
    try:
        from pytest_socket import enable_socket
        enable_socket()
    except ImportError:
        pass

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

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the custom_components dir."""
    yield

