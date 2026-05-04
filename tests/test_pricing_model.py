import pandas as pd
from src.pricing_model import calculate_deviation, apply_review_flag


def test_deviation_calculation():
    df = pd.DataFrame({
        "item_id": ["A"],
        "observed_value": [110],
        "model_value": [100]
    })

    result = calculate_deviation(df)
    assert round(result["deviation"].iloc[0], 2) == 0.10


def test_review_flag():
    df = pd.DataFrame({
        "item_id": ["A"],
        "observed_value": [110],
        "model_value": [100]
    })

    df = calculate_deviation(df)
    df = apply_review_flag(df, threshold=0.05)

    assert df["review_flag"].iloc[0] == "Review"
