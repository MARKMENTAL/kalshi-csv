import pytest
from pathlib import Path


@pytest.fixture
def sample_csv():
    """Returns the path to the synthetic test CSV fixture."""
    return str(Path(__file__).parent / "fixtures" / "sample.csv")
