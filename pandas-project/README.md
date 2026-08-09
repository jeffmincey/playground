# sales-report

A small pandas project that reads a sales CSV and prints three summary tables:
revenue by region, revenue by month, and the top products.

It is deliberately plain — a loader, a module of aggregations, a CLI and tests —
so it works as a starting point for any "clean a CSV, then aggregate it" job.

## Requirements

- Python 3.11+
- pandas 2.2+ (installed below)

## Installation

With pixi (recommended in this repo — also what notebook kernels use):

```bash
cd pandas-project
pixi install
pixi run report        # summarize the sample CSV
pixi run test          # run the test suite
```

Or as a plain pip package:

```bash
cd pandas-project
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
sales-report data/sales_sample.csv
```

Equivalent, without installing the package:

```bash
PYTHONPATH=src python3 -m sales_report data/sales_sample.csv
```

Output:

```
22 orders, 4,711.30 total revenue

Revenue By Region
-----------------
region  orders  units  revenue  share
  East       6    101  1463.57   0.31
  West       5     56   1314.5   0.28
 North       6     90   1161.3   0.25
 South       5     52   771.93   0.16

Monthly Revenue
---------------
     month  revenue  growth
2024-01-01   454.55       —
2024-02-01  1084.82    1.39
...
```

Flags:

| Flag | Default | Description |
| --- | --- | --- |
| `--top N` | `5` | How many products to list |
| `--out DIR` | none | Also write each table to `DIR` as a CSV |

The sample file has 25 rows but only 22 are reported: three carry an unparseable
date, no unit count, or no price, and the loader drops them rather than guess.

## Input format

| Column | Type | Notes |
| --- | --- | --- |
| `order_id` | string | Counted to get the order total per group |
| `order_date` | date | Anything `pd.to_datetime` accepts |
| `region` | string | Trimmed and title-cased, so `north ` and `NORTH` agree |
| `product` | string | Trimmed |
| `units` | integer | Rows without a value are dropped |
| `unit_price` | float | Rows without a value are dropped |

`revenue` is derived as `units * unit_price`; do not supply it.

## Using it as a library

```python
from sales_report import load_sales, revenue_by_region

sales = load_sales("data/sales_sample.csv")
print(revenue_by_region(sales))
```

## Development

```bash
pytest          # 25 tests
ruff check .    # lint
```

## Project layout

```
pandas-project/
├── pyproject.toml           # dependencies, console script, pytest + ruff config
├── data/
│   └── sales_sample.csv     # sample input, including three unusable rows
├── src/sales_report/
│   ├── loader.py            # read + clean the CSV, add `revenue`
│   ├── transform.py         # the aggregations
│   ├── cli.py               # argument parsing and printing
│   └── __main__.py          # `python -m sales_report`
└── tests/
    ├── conftest.py          # loads the sample file once per session
    ├── test_loader.py
    ├── test_transform.py
    └── test_cli.py
```
