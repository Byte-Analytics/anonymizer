import pathlib

import pytest


@pytest.fixture
def fake_fs(fs):
    fs.add_real_directory(pathlib.Path(__file__).parent / 'data')
    fs.add_real_file(pathlib.Path(__file__).parent.parent / 'config.toml')
    yield fs
