"""Aggregations over a frame produced by `load_sales`."""

from __future__ import annotations

import pandas as pd


def revenue_by_region(sales: pd.DataFrame) -> pd.DataFrame:
    """Revenue, units and order count per region, biggest region first."""
    summary = sales.groupby("region", as_index=False, observed=True).agg(
        orders=("order_id", "count"),
        units=("units", "sum"),
        revenue=("revenue", "sum"),
    )
    summary["share"] = summary["revenue"] / summary["revenue"].sum()
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def monthly_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    """Revenue per calendar month, oldest first, with month-over-month growth.

    `growth` is null for the first month, which has nothing to compare against.
    """
    monthly = (
        sales.set_index("order_date")
        .resample("MS")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"order_date": "month"})
    )
    monthly["growth"] = monthly["revenue"].pct_change()
    return monthly


def top_products(sales: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """The `limit` highest-revenue products, with average revenue per order."""
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")

    summary = sales.groupby("product", as_index=False, observed=True).agg(
        orders=("order_id", "count"),
        units=("units", "sum"),
        revenue=("revenue", "sum"),
    )
    summary["revenue_per_order"] = summary["revenue"] / summary["orders"]
    return summary.sort_values("revenue", ascending=False).head(limit).reset_index(drop=True)
