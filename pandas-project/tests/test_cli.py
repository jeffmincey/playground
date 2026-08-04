import pandas as pd
import pytest

from sales_report.cli import main


def test_sample_run_succeeds_and_prints_every_table(sample_csv, capsys):
    assert main([str(sample_csv)]) == 0

    out = capsys.readouterr().out
    assert "22 orders" in out
    for heading in ("Revenue By Region", "Monthly Revenue", "Top Products"):
        assert heading in out


def test_top_flag_limits_the_product_table(sample_csv, capsys):
    main([str(sample_csv), "--top", "1"])

    products = capsys.readouterr().out.split("Top Products")[1].strip().splitlines()
    # A dashed rule, a header row, then exactly one product.
    assert len(products) == 3


def test_out_flag_writes_one_csv_per_table(sample_csv, tmp_path, capsys):
    destination = tmp_path / "nested" / "reports"
    assert main([str(sample_csv), "--out", str(destination)]) == 0
    capsys.readouterr()

    written = sorted(path.name for path in destination.glob("*.csv"))
    assert written == ["monthly_revenue.csv", "revenue_by_region.csv", "top_products.csv"]
    assert not pd.read_csv(destination / "revenue_by_region.csv").empty


def test_missing_file_exits_nonzero_without_a_traceback(tmp_path, capsys):
    assert main([str(tmp_path / "nope.csv")]) == 1
    assert "no such file" in capsys.readouterr().out


def test_file_with_no_usable_rows_exits_nonzero(tmp_path, capsys):
    path = tmp_path / "empty.csv"
    path.write_text("order_id,order_date,region,product,units,unit_price\nA-1,bad,North,Widget,,\n")

    assert main([str(path)]) == 1
    assert "no usable rows" in capsys.readouterr().out


def test_bad_schema_exits_nonzero(tmp_path, capsys):
    path = tmp_path / "partial.csv"
    path.write_text("order_id,region\nA-1,North\n")

    assert main([str(path)]) == 1
    assert "missing columns" in capsys.readouterr().out


def test_unparseable_argument_still_exits(sample_csv):
    with pytest.raises(SystemExit):
        main([str(sample_csv), "--top", "not-a-number"])
