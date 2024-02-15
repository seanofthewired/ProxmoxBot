import logging
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_logging():
    with patch("logging.info"), patch("logging.error"):
        yield


@pytest.fixture
def mock_time():
    with patch("time.time", return_value=1000):
        yield 1000
