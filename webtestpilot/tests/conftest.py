import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import sys

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from executor.assertion_api.session import Session
from executor.assertion_api.state import State
from executor.assertion_api.element import Element
from config import Config


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page object."""
    page = Mock()
    page.is_closed.return_value = False
    page.url = "https://example.com"
    page.title.return_value = "Test Page"
    page.content.return_value = "<html><body>Test content</body></html>"
    page.screenshot.return_value = b"fake_screenshot_data"
    page.evaluate.return_value = []
    return page


@pytest.fixture
def mock_config():
    """Create a mock Config object."""
    config = Mock(spec=Config)
    config.page_reidentification = "mock_registry"
    return config


@pytest.fixture
def mock_session(mock_page, mock_config):
    """Create a mock Session object with necessary attributes."""
    session = Mock(spec=Session)
    session.page = mock_page
    session.config = mock_config
    session.history = []
    session.step_counter = 0

    # Mock the methods that might be called
    session.capture_state = Mock()
    session.capture_elements = Mock(return_value={})
    session.get_history = Mock(return_value=[])

    return session


@pytest.fixture
def mock_state():
    """Create a mock State object."""
    state = Mock(spec=State)
    state.page_id = "test_page_1"
    state.url = "https://example.com"
    state.title = "Test Page"
    state.description = "A test page"
    state.layout = "Test layout"
    state.elements = {}
    state.screenshot = "base64_screenshot"
    state.prev_action = None
    state.xml_tree = []
    return state


@pytest.fixture
def mock_element():
    """Create a mock Element object."""
    element = Mock(spec=Element)
    element.id = 1
    element.tag_name = "div"
    element.text = "Test element"
    element.attributes = {"class": "test-class"}
    element.visible = True
    element.x = 100
    element.y = 200
    element.width = 300
    element.height = 50
    element.parentId = None
    element.children = []
    return element
