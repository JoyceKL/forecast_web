import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, render_template
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

from utils.preprocessing import preprocess_dataframe
from utils.chart_utils import plot_forecast

forecast_bp = Blueprint("forecast_bp", __name__)

MODEL_DIR = "models"
DOWNLOAD_DIR = "downloads"
CHART_DIR = os.path.join("static", "charts")
CHART_FILE = "forecast.png"


@forecast_bp.route("/forecast", methods=["POST"])
def run_model():
    """Upload data, run selected model and store results."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    model_name = request.form.get("model")
    if not model_name:
        return jsonify({"error": "No model selected"}), 400

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        X, dates = preprocess_dataframe(df)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    model_path = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        return jsonify({"error": "Model not found"}), 400

    if model_path.endswith((".pkl", ".joblib")):
        model = joblib.load(model_path)
        preds = model.predict(X).reshape(-1).tolist()
    elif model_path.endswith(".h5"):
        model = load_model(model_path)
        preds = model.predict(X).reshape(-1).tolist()
    else:
        return jsonify({"error": "Unsupported model format"}), 400

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    result_df = pd.DataFrame({"Date": dates, "Predicted": preds})
    result = {"dates": dates, "predicted": preds}
    if "Value" in df.columns:
        result_df["Actual"] = df["Value"].tolist()
        result["actual"] = df["Value"].tolist()

    csv_path = os.path.join(DOWNLOAD_DIR, "forecast.csv")
    excel_path = os.path.join(DOWNLOAD_DIR, "forecast.xlsx")
    result_df.to_csv(csv_path, index=False)
    result_df.to_excel(excel_path, index=False)

    chart_path = os.path.join(CHART_DIR, CHART_FILE)
    actual_vals = result_df.get("Actual").tolist() if "Actual" in result_df.columns else None
    plot_forecast(dates, actual_vals, preds, save_path=chart_path)

    history_file = os.path.join(DOWNLOAD_DIR, "history.json")
    history = []
    if os.path.exists(history_file):
        with open(history_file) as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    history.append({"timestamp": datetime.utcnow().isoformat()})
    with open(history_file, "w") as f:
        json.dump(history, f)

    return jsonify(result)


@forecast_bp.route("/forecast/result")
def visualize_result():
    """Render forecast result table and chart."""
    csv_path = os.path.join(DOWNLOAD_DIR, "forecast.csv")
    preview = []
    if os.path.exists(csv_path):
        preview = pd.read_csv(csv_path).head().to_dict(orient="records")
    return render_template("forecast_result.html", preview=preview)


@forecast_bp.route("/forecast/download/<ftype>")
def download_file(ftype: str):
    """Download forecast results as csv or excel."""
    filename = "forecast.csv" if ftype == "csv" else "forecast.xlsx"
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


@forecast_bp.route("/forecast/download/chart")
def download_chart():
    """Download forecast chart PNG."""
    return send_from_directory(CHART_DIR, CHART_FILE, as_attachment=True)
