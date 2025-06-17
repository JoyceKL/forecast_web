import os
import json
from flask import Blueprint, request, render_template, redirect, send_from_directory
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

forecast_bp = Blueprint("forecast_bp", __name__)

DATA_DIR = os.path.join("data", "processed")
RESULT_DIR = "results"


def _load_data():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Missing train.csv or test.csv in data/processed")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    return train_df, test_df


def _linear_forecast(train, test, seq_len):
    series = train["Value"].values
    X, y = [], []
    for i in range(seq_len, len(series)):
        X.append(series[i-seq_len:i])
        y.append(series[i])
    model = LinearRegression()
    model.fit(np.array(X), np.array(y))

    all_vals = np.concatenate([series[-seq_len:], test["Value"].values])
    preds = []
    for i in range(seq_len, seq_len + len(test)):
        x = all_vals[i-seq_len:i].reshape(1, -1)
        pred = model.predict(x)[0]
        preds.append(pred)
    return preds


def _arima_forecast(train, test, seq_len):
    model = ARIMA(train["Value"], order=(max(1, seq_len), 1, 0)).fit()
    preds = model.forecast(steps=len(test))
    return preds.tolist()


@forecast_bp.route("/forecast", methods=["GET", "POST"])
def forecast_page():
    if request.method == "GET":
        return render_template("forecast.html")

    model_name = request.form.get("model") or "linear"
    seq_len = int(request.form.get("seq_len", 3))
    _ = int(request.form.get("epochs", 10))  # unused but parsed
    train_df, test_df = _load_data()

    if model_name == "arima":
        preds = _arima_forecast(train_df, test_df, seq_len)
    else:
        preds = _linear_forecast(train_df, test_df, seq_len)

    mape = mean_absolute_percentage_error(test_df["Value"], preds)
    rmse = mean_squared_error(test_df["Value"], preds, squared=False)

    os.makedirs(RESULT_DIR, exist_ok=True)
    result_df = pd.DataFrame({
        "Date": test_df["Date"],
        "Actual": test_df["Value"],
        "Predicted": preds,
    })
    result_df.to_csv(os.path.join(RESULT_DIR, "forecast.csv"), index=False)
    with open(os.path.join(RESULT_DIR, "metrics.json"), "w") as f:
        json.dump({"MAPE": mape, "RMSE": rmse}, f)

    return redirect("/forecast/result")


@forecast_bp.route("/forecast/result")
def show_result():
    csv_path = os.path.join(RESULT_DIR, "forecast.csv")
    metrics_path = os.path.join(RESULT_DIR, "metrics.json")
    preview = []
    metrics = {}
    if os.path.exists(csv_path):
        preview = pd.read_csv(csv_path).head().to_dict(orient="records")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)
    return render_template("result.html", preview=preview, metrics=metrics)


@forecast_bp.route("/forecast/download/<ftype>")
def download_file(ftype: str):
    filename = "forecast.csv" if ftype == "csv" else "metrics.json"
    return send_from_directory(RESULT_DIR, filename, as_attachment=True)

