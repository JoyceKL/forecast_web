import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def preprocess_dataframe(df: pd.DataFrame):
    """Parse datetime, add time features and scale numeric columns.

    Returns scaled feature matrix X and list of dates as strings.
    """
    if "Date" not in df.columns:
        raise ValueError("Input data must contain a 'Date' column")

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()

    # add basic time features
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    feature_cols = df.drop(columns=["Date", "Value"], errors="ignore")
    scaler = MinMaxScaler()
    X = scaler.fit_transform(feature_cols)
    return X, dates
