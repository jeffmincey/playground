"""Read the sales CSV and hand back a frame the transforms can trust."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# The columns every input file must provide, and the dtype each is read as.
COLUMNS: dict[str, str] = {
    "order_id": "string",
    "order_date": "string",  # parsed to datetime after read
    "region": "string",
    "product": "string",
    "units": "Int64",
    "unit_price": "Float64",
}


class SchemaError(ValueError):
    """Raised when the input file does not match COLUMNS."""


def load_sales(path: str | Path) -> pd.DataFrame:
    """Load a sales CSV into a cleaned frame with a `revenue` column.

    Cleaning steps, in order:

    1. Check that every column in `COLUMNS` is present.
    2. Parse `order_date` to datetime; unparseable dates become NaT.
    3. Trim and title-case `region` so "north ", "North" and "NORTH" agree.
    4. Drop rows missing a date, units or price — they cannot be summed.
    5. Add `revenue = units * unit_price`.
    """
    frame = pd.read_csv(path, dtype=COLUMNS)

    missing = [column for column in COLUMNS if column not in frame.columns]
    if missing:
        raise SchemaError(f"{Path(path).name} is missing columns: {', '.join(missing)}")

    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce")
    frame["region"] = frame["region"].str.strip().str.title()
    frame["product"] = frame["product"].str.strip()

    frame = frame.dropna(subset=["order_date", "units", "unit_price"])
    frame["revenue"] = frame["units"] * frame["unit_price"]

    return frame.reset_index(drop=True)
