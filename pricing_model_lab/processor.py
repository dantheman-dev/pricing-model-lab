"""Core processing logic for the pricing model lab."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"item_id", "observed_value", "model_value"}
DEFAULT_THRESHOLD = 0.03  # 3%


def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame.

    Raises
    ------
    FileNotFoundError
        If *filepath* does not exist.
    ValueError
        If required columns are missing.
    """
    df = pd.read_csv(filepath)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    return df


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Validate that numeric columns are numeric and contain no missing values.

    Returns a cleaned copy with numeric columns cast to float.

    Raises
    ------
    ValueError
        If non-numeric data or missing values are found in *observed_value*
        or *model_value*.
    """
    df = df.copy()

    for col in ("observed_value", "model_value"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

        if df[col].isna().any():
            raise ValueError(
                f"Column '{col}' contains missing or non-numeric values."
            )

    if (df["model_value"] == 0).any():
        raise ValueError(
            "Column 'model_value' contains zero values; deviation is undefined."
        )

    if df["item_id"].isna().any():
        raise ValueError("Column 'item_id' contains missing values.")

    return df


def calculate_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Add a *deviation* column: (observed_value - model_value) / model_value."""
    df = df.copy()
    df["deviation"] = (df["observed_value"] - df["model_value"]) / df["model_value"]
    return df


def add_review_flag(
    df: pd.DataFrame, threshold: float = DEFAULT_THRESHOLD
) -> pd.DataFrame:
    """Add a boolean *review_flag* column.

    A row is flagged when the absolute deviation exceeds *threshold*.
    """
    if threshold < 0:
        raise ValueError("threshold must be non-negative.")

    df = df.copy()
    df["review_flag"] = df["deviation"].abs() > threshold
    return df


def sort_by_abs_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Return *df* sorted by absolute deviation in descending order."""
    df = df.copy()
    df["_abs_deviation"] = df["deviation"].abs()
    df = df.sort_values("_abs_deviation", ascending=False).drop(
        columns=["_abs_deviation"]
    )
    return df.reset_index(drop=True)


def process(
    input_path: str,
    output_path: str,
    threshold: float = DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """Run the full pipeline and write results to *output_path*.

    Parameters
    ----------
    input_path:
        Path to the input CSV file.
    output_path:
        Path where the output CSV will be written.
    threshold:
        Absolute deviation threshold for the review flag (default 3 %).

    Returns
    -------
    pd.DataFrame
        The processed DataFrame that was written to *output_path*.
    """
    df = load_csv(input_path)
    df = validate(df)
    df = calculate_deviation(df)
    df = add_review_flag(df, threshold=threshold)
    df = sort_by_abs_deviation(df)
    df.to_csv(output_path, index=False)
    return df
