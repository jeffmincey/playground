"""Command line entry point: `sales-report data/sales_sample.csv`."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from sales_report.loader import SchemaError, load_sales
from sales_report.transform import monthly_revenue, revenue_by_region, top_products


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales-report",
        description="Summarise a sales CSV by region, month and product.",
    )
    parser.add_argument("csv", type=Path, help="path to the sales CSV")
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="how many products to list (default: 5)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        metavar="DIR",
        help="also write each table to DIR as a CSV file",
    )
    return parser


def _print_table(title: str, table: pd.DataFrame) -> None:
    """Print one table, rounding the numeric columns and leaving dates alone."""
    numeric = list(table.select_dtypes("number"))
    rounded = table.round({column: 2 for column in numeric})
    # `na_rep` below only replaces NaN, not pandas' NA, so cast the columns with
    # gaps in them to plain floats. Gap-free integer columns keep their dtype.
    gapped = {column: "float64" for column in numeric if rounded[column].isna().any()}
    rounded = rounded.astype(gapped)
    print(f"\n{title}")
    print("-" * len(title))
    print(rounded.to_string(index=False, na_rep="—"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        sales = load_sales(args.csv)
    except FileNotFoundError:
        print(f"error: no such file: {args.csv}")
        return 1
    except (SchemaError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    if sales.empty:
        print(f"error: {args.csv} has no usable rows")
        return 1

    tables = {
        "revenue_by_region": revenue_by_region(sales),
        "monthly_revenue": monthly_revenue(sales),
        "top_products": top_products(sales, limit=args.top),
    }

    print(f"{len(sales)} orders, {sales['revenue'].sum():,.2f} total revenue")
    for name, table in tables.items():
        _print_table(name.replace("_", " ").title(), table)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for name, table in tables.items():
            table.to_csv(args.out / f"{name}.csv", index=False)
        print(f"\nWrote {len(tables)} CSV files to {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
