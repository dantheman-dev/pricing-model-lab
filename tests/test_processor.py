"""Tests for pricing_model_lab.processor."""

from __future__ import annotations

import io
import textwrap

import pandas as pd
import pytest

from pricing_model_lab.processor import (
    add_review_flag,
    calculate_deviation,
    load_csv,
    process,
    sort_by_abs_deviation,
    validate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(
    item_ids=("A", "B", "C"),
    observed=(102.0, 98.0, 110.0),
    model=(100.0, 100.0, 100.0),
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "item_id": list(item_ids),
            "observed_value": list(observed),
            "model_value": list(model),
        }
    )


# ---------------------------------------------------------------------------
# load_csv
# ---------------------------------------------------------------------------

def test_load_csv_success(tmp_path):
    csv_content = "item_id,observed_value,model_value\nA,100,100\n"
    p = tmp_path / "data.csv"
    p.write_text(csv_content)
    df = load_csv(str(p))
    assert list(df.columns) == ["item_id", "observed_value", "model_value"]
    assert len(df) == 1


def test_load_csv_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("item_id,observed_value\nA,100\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_csv(str(p))


def test_load_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_csv("/nonexistent/path/file.csv")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def test_validate_success():
    df = _make_df()
    result = validate(df)
    assert result["observed_value"].dtype == float
    assert result["model_value"].dtype == float


def test_validate_non_numeric_observed():
    df = _make_df(observed=("bad", 98.0, 110.0))
    with pytest.raises(ValueError, match="observed_value"):
        validate(df)


def test_validate_non_numeric_model():
    df = _make_df(model=(100.0, "n/a", 100.0))
    with pytest.raises(ValueError, match="model_value"):
        validate(df)


def test_validate_missing_observed():
    df = _make_df(observed=(None, 98.0, 110.0))
    with pytest.raises(ValueError, match="observed_value"):
        validate(df)


def test_validate_zero_model_value():
    df = _make_df(model=(0.0, 100.0, 100.0))
    with pytest.raises(ValueError, match="zero values"):
        validate(df)


def test_validate_missing_item_id():
    df = _make_df(item_ids=(None, "B", "C"))
    with pytest.raises(ValueError, match="item_id"):
        validate(df)


# ---------------------------------------------------------------------------
# calculate_deviation
# ---------------------------------------------------------------------------

def test_calculate_deviation_values():
    df = _make_df(observed=(110.0, 90.0, 100.0), model=(100.0, 100.0, 100.0))
    result = calculate_deviation(df)
    assert "deviation" in result.columns
    assert result.loc[0, "deviation"] == pytest.approx(0.10)
    assert result.loc[1, "deviation"] == pytest.approx(-0.10)
    assert result.loc[2, "deviation"] == pytest.approx(0.00)


def test_calculate_deviation_does_not_mutate():
    df = _make_df()
    original_cols = list(df.columns)
    calculate_deviation(df)
    assert list(df.columns) == original_cols


# ---------------------------------------------------------------------------
# add_review_flag
# ---------------------------------------------------------------------------

def test_add_review_flag_default_threshold():
    df = _make_df(observed=(103.1, 96.9, 100.0), model=(100.0, 100.0, 100.0))
    df = calculate_deviation(df)
    result = add_review_flag(df)
    # deviations: 0.031, -0.031, 0.0
    assert result.loc[0, "review_flag"]
    assert result.loc[1, "review_flag"]
    assert not result.loc[2, "review_flag"]


def test_add_review_flag_custom_threshold():
    df = _make_df(observed=(105.0, 100.0, 100.0), model=(100.0, 100.0, 100.0))
    df = calculate_deviation(df)
    result = add_review_flag(df, threshold=0.10)
    # deviation 5% < 10% → not flagged
    assert not result.loc[0, "review_flag"]


def test_add_review_flag_negative_threshold():
    df = calculate_deviation(_make_df())
    with pytest.raises(ValueError, match="non-negative"):
        add_review_flag(df, threshold=-0.01)


# ---------------------------------------------------------------------------
# sort_by_abs_deviation
# ---------------------------------------------------------------------------

def test_sort_by_abs_deviation_order():
    df = _make_df(observed=(101.0, 120.0, 95.0), model=(100.0, 100.0, 100.0))
    df = calculate_deviation(df)
    result = sort_by_abs_deviation(df)
    abs_devs = result["deviation"].abs().tolist()
    assert abs_devs == sorted(abs_devs, reverse=True)


def test_sort_by_abs_deviation_no_extra_columns():
    df = calculate_deviation(_make_df())
    result = sort_by_abs_deviation(df)
    assert "_abs_deviation" not in result.columns


# ---------------------------------------------------------------------------
# process (end-to-end)
# ---------------------------------------------------------------------------

def test_process_end_to_end(tmp_path):
    csv_content = textwrap.dedent("""\
        item_id,observed_value,model_value
        X,110,100
        Y,100,100
        Z,85,100
    """)
    input_path = tmp_path / "input.csv"
    input_path.write_text(csv_content)
    output_path = tmp_path / "output.csv"

    result = process(str(input_path), str(output_path), threshold=0.03)

    assert output_path.exists()
    written = pd.read_csv(str(output_path))
    assert list(written.columns) == [
        "item_id", "observed_value", "model_value", "deviation", "review_flag"
    ]
    # Z has largest abs deviation (−15%), X second (10%), Y zero
    assert written.loc[0, "item_id"] == "Z"
    assert written.loc[1, "item_id"] == "X"
    assert written.loc[2, "item_id"] == "Y"
    # Z and X should be flagged; Y should not
    assert written.loc[0, "review_flag"]
    assert written.loc[1, "review_flag"]
    assert not written.loc[2, "review_flag"]
    # row count matches
    assert len(result) == 3
