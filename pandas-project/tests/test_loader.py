import pandas as pd
import pytest

from sales_report.loader import COLUMNS, SchemaError, load_sales


def test_all_declared_columns_survive_loading(sales: pd.DataFrame):
    assert set(COLUMNS) <= set(sales.columns)


def test_order_date_is_parsed(sales: pd.DataFrame):
    assert pd.api.types.is_datetime64_any_dtype(sales["order_date"])
    assert sales["order_date"].notna().all()


def test_region_casing_and_whitespace_are_normalised(sales: pd.DataFrame):
    # The sample file contains "south", "WEST" and "North " alongside clean values.
    assert set(sales["region"]) == {"North", "South", "East", "West"}


def test_rows_without_usable_numbers_are_dropped(sales: pd.DataFrame):
    # A-1021 has a bad date, A-1022 no units, A-1023 no price: 25 rows in, 22 out.
    assert len(sales) == 22
    dropped = {"A-1021", "A-1022", "A-1023"}
    assert dropped.isdisjoint(set(sales["order_id"]))


def test_revenue_is_units_times_price(sales: pd.DataFrame):
    expected = sales["units"] * sales["unit_price"]
    pd.testing.assert_series_equal(sales["revenue"], expected, check_names=False)


def test_missing_column_raises_schema_error(tmp_path):
    path = tmp_path / "partial.csv"
    path.write_text("order_id,order_date,region\nA-1,2024-01-01,North\n")

    with pytest.raises(SchemaError, match="missing columns"):
        load_sales(path)


def test_index_is_reset_after_dropping_rows(sales: pd.DataFrame):
    assert list(sales.index) == list(range(len(sales)))
