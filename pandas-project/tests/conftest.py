from pathlib import Path

import pytest

from sales_report.loader import load_sales

SAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sales_sample.csv"


@pytest.fixture(scope="session")
def sample_csv() -> Path:
    return SAMPLE_CSV


@pytest.fixture(scope="session")
def sales(sample_csv: Path):
    return load_sales(sample_csv)
