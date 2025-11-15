"""
Generic test template for Python projects.
Compatible with pytest and pytest-asyncio.
"""

import pytest

# Example synchronous test
def test_basic_math():
    """Simple sanity test to ensure pytest runs correctly."""
    assert 2 + 2 == 4


# Example function import test (replace with your module)
def test_imports():
    """Ensure utils module imports correctly."""
    import utils  # noqa: F401 # type: ignore[import-unused]


# Example of using fixtures
@pytest.fixture
def sample_data():
    return {"name": "Silver", "role": "engineer"}


def test_sample_data_fixture(sample_data):
    """Test using a pytest fixture."""
    assert "name" in sample_data
    assert sample_data["role"] == "engineer"


# Example async test (requires pytest-asyncio)
@pytest.mark.asyncio
async def test_async_behavior():
    """Async test example."""
    async def fake_task():
        return 42

    result = await fake_task()
    assert result == 42
