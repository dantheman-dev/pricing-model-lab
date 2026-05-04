import pandas as pd


REQUIRED_COLUMNS = ["item_id", "observed_value", "model_value"]


def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    validate_columns(df)
    validate_types(df)
    return df


def validate_columns(df: pd.DataFrame):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_types(df: pd.DataFrame):
    for col in ["observed_value", "model_value"]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(f"Column '{col}' must be numeric")


def calculate_deviation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["deviation"] = (df["observed_value"] - df["model_value"]) / df["model_value"]
    return df


def apply_review_flag(df: pd.DataFrame, threshold: float = 0.03) -> pd.DataFrame:
    df = df.copy()
    df["review_flag"] = df["deviation"].abs().apply(
        lambda x: "Review" if x > threshold else "OK"
    )
    return df


def process(file_path: str, output_path: str, threshold: float = 0.03):
    df = load_data(file_path)
    df = calculate_deviation(df)
    df = apply_review_flag(df, threshold)

    df = df.sort_values(by="deviation", key=lambda x: x.abs(), ascending=False)

    df.to_csv(output_path, index=False)
    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pricing Model Lab CLI")
    parser.add_argument("input", help="Input CSV file path")
    parser.add_argument("output", help="Output CSV file path")
    parser.add_argument("--threshold", type=float, default=0.03)

    args = parser.parse_args()

    process(args.input, args.output, args.threshold)
