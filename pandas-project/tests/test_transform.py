import pandas as pd
import pytest

from sales_report.transform import monthly_revenue, revenue_by_region, top_products


def test_region_summary_covers_every_region_once(sales: pd.DataFrame):
    summary = revenue_by_region(sales)
    assert len(summary) == sales["region"].nunique()
    assert not summary["region"].duplicated().any()


def test_region_summary_is_sorted_by_revenue(sales: pd.DataFrame):
    revenue = revenue_by_region(sales)["revenue"]
    assert revenue.is_monotonic_decreasing


def test_region_shares_sum_to_one(sales: pd.DataFrame):
    assert revenue_by_region(sales)["share"].sum() == pytest.approx(1.0)


def test_region_revenue_totals_match_the_input(sales: pd.DataFrame):
    assert revenue_by_region(sales)["revenue"].sum() == pytest.approx(sales["revenue"].sum())


def test_monthly_revenue_is_chronological_and_complete(sales: pd.DataFrame):
    monthly = monthly_revenue(sales)
    assert monthly["month"].is_monotonic_increasing
    # The sample spans January to May 2024 with no empty months.
    assert len(monthly) == 5
    assert monthly["revenue"].sum() == pytest.approx(sales["revenue"].sum())


def test_first_month_has_no_growth_figure(sales: pd.DataFrame):
    growth = monthly_revenue(sales)["growth"]
    assert pd.isna(growth.iloc[0])
    assert growth.iloc[1:].notna().all()


def test_top_products_respects_the_limit(sales: pd.DataFrame):
    assert len(top_products(sales, limit=2)) == 2


def test_limit_larger_than_the_catalogue_returns_everything(sales: pd.DataFrame):
    assert len(top_products(sales, limit=100)) == sales["product"].nunique()


def test_top_products_is_sorted_by_revenue(sales: pd.DataFrame):
    assert top_products(sales, limit=4)["revenue"].is_monotonic_decreasing


def test_revenue_per_order_is_revenue_over_orders(sales: pd.DataFrame):
    products = top_products(sales)
    expected = products["revenue"] / products["orders"]
    pd.testing.assert_series_equal(products["revenue_per_order"], expected, check_names=False)


def test_limit_below_one_is_rejected(sales: pd.DataFrame):
    with pytest.raises(ValueError, match="at least 1"):
        top_products(sales, limit=0)
