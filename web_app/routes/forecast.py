import os
import json
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, send_from_directory
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from fpdf import FPDF
from utils.chart_utils import plot_forecast

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


def _export_pdf(df: pd.DataFrame, save_path: str) -> None:
    """Save forecast DataFrame to a simple PDF table."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Forecast Result", ln=True, align="C")
    col_width = 40
    headers = df.columns.tolist()
    for h in headers:
        pdf.cell(col_width, 10, h, border=1)
    pdf.ln()
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(round(item, 4)) if isinstance(item, (float, int)) else str(item), border=1)
        pdf.ln()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    pdf.output(save_path)


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
    result_df["Residual"] = result_df["Actual"] - result_df["Predicted"]
    chart_path = os.path.join("static", "charts", "forecast.png")
    plot_forecast(result_df["Date"].tolist(), result_df["Actual"].tolist(), preds, save_path=chart_path)
    csv_path = os.path.join(RESULT_DIR, "forecast.csv")
    pdf_path = os.path.join(RESULT_DIR, "forecast.pdf")
    result_df.to_csv(csv_path, index=False)
    _export_pdf(result_df, pdf_path)
    with open(os.path.join(RESULT_DIR, "metrics.json"), "w") as f:
        json.dump({"MAPE": mape, "RMSE": rmse, "model": model_name, "params": {"seq_len": seq_len}}, f)

    history_path = os.path.join(RESULT_DIR, "history.json")
    history = []
    if os.path.exists(history_path):
        with open(history_path) as hf:
            try:
                history = json.load(hf)
            except json.JSONDecodeError:
                history = []
    history.append({
        "data_file": "train.csv,test.csv",
        "model": model_name,
        "params": {"seq_len": seq_len},
        "MAPE": mape,
        "RMSE": rmse,
        "timestamp": datetime.utcnow().isoformat()
    })
    with open(history_path, "w") as hf:
        json.dump(history, hf)

    return redirect("/forecast/result")


@forecast_bp.route("/forecast/result")
def show_result():
    csv_path = os.path.join(RESULT_DIR, "forecast.csv")
    metrics_path = os.path.join(RESULT_DIR, "metrics.json")
    rows = []
    metrics = {}
    if os.path.exists(csv_path):
        rows = pd.read_csv(csv_path).to_dict(orient="records")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)
    chart_url = None
    if os.path.exists(os.path.join("static", "charts", "forecast.png")):
        chart_url = "/static/charts/forecast.png"
    return render_template("result.html", rows=rows, metrics=metrics, chart_url=chart_url)


@forecast_bp.route("/forecast/download/<ftype>")
def download_file(ftype: str):
    if ftype == "csv":
        filename = "forecast.csv"
    elif ftype == "pdf":
        filename = "forecast.pdf"
    else:
        filename = "metrics.json"
    return send_from_directory(RESULT_DIR, filename, as_attachment=True)


@forecast_bp.route("/history")
def history_page():
    """Display forecasting history from results/history.json."""
    history_path = os.path.join(RESULT_DIR, "history.json")
    records = []
    if os.path.exists(history_path):
        with open(history_path) as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []
    return render_template("history.html", records=records)

