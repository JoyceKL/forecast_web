import os
from typing import Tuple, Dict, Optional
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def full_pipeline(
    df: pd.DataFrame,
    use_ssa: bool = False,
    use_wavelet: bool = False,
    use_rolling: bool = False,
    lag: int = 1,
    split_ratio: float = 0.7,
    split_date: Optional[str] = None,
    scaler: str = "minmax",
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Dict[str, Dict[str, float]]]]:
    """Run cleaning, feature extraction, splitting and scaling pipeline.

    Parameters
    ----------
    df: pd.DataFrame
        Raw input data containing a 'Date' column and optionally 'Value'.
    use_ssa, use_wavelet: bool
        Placeholder options for signal processing steps.
    use_rolling: bool
        Whether to compute rolling mean feature.
    lag: int
        Number of lag features to create from 'Value'.
    split_ratio: float
        Train/test split ratio if split_date is not provided.
    split_date: str, optional
        Specific date string to split train/test.
    scaler: str
        Either 'minmax' or 'standard'.

    Returns
    -------
    train_df, test_df, stats
    """
    df = df.copy()

    # ---- Step 1: Cleaning ----
    if "Date" not in df.columns:
        raise ValueError("Data must contain 'Date' column")
    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
    # drop rows where all numeric values are zero
    num_cols = df.select_dtypes(include="number").columns
    df = df.loc[~(df[num_cols] == 0).all(axis=1)]

    # combine duplicate IDs etc. - placeholder

    # ---- Step 2: Signal processing (placeholders) ----
    if use_ssa or use_wavelet:
        # actual implementation would modify df based on options
        pass

    # ---- Step 3: Detrend/seasonal adjust ----
    if "Value" in df.columns:
        df["Value_detrend"] = df["Value"].diff().fillna(0)

    # ---- Step 4: Feature extraction ----
    if "Value" in df.columns:
        for i in range(1, lag + 1):
            df[f"lag_{i}"] = df["Value"].shift(i)
        if use_rolling:
            df["rolling_mean"] = df["Value"].rolling(window=3).mean()
    df.dropna(inplace=True)

    # ---- Step 5: Train/Test split ----
    if split_date:
        split_dt = pd.to_datetime(split_date)
        train_df = df[df["Date"] <= split_dt]
        test_df = df[df["Date"] > split_dt]
    else:
        idx = int(len(df) * split_ratio)
        train_df = df.iloc[:idx]
        test_df = df.iloc[idx:]

    # ---- Step 6: Scaling ----
    scaler_cls = MinMaxScaler if scaler == "minmax" else StandardScaler
    scaler_obj = scaler_cls()
    num_cols = train_df.select_dtypes(include="number").columns
    scaler_obj.fit(train_df[num_cols])
    train_scaled = train_df.copy()
    test_scaled = test_df.copy()
    train_scaled[num_cols] = scaler_obj.transform(train_df[num_cols])
    test_scaled[num_cols] = scaler_obj.transform(test_df[num_cols])

    before_stats = train_df[num_cols].agg(["min", "max", "mean"]).to_dict()
    after_stats = train_scaled[num_cols].agg(["min", "max", "mean"]).to_dict()
    stats = {"before": before_stats, "after": after_stats}

    return train_scaled, test_scaled, stats
