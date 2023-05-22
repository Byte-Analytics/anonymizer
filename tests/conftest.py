from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_worker() -> MagicMock:
    # Fake worker that will return our mapping.
    worker = MagicMock()
    # No-op encoder ensures that we should get exactly the same file on the output.
    worker.encode_value = MagicMock(side_effect=lambda x: x)
    worker.save_output = MagicMock()
    return worker
