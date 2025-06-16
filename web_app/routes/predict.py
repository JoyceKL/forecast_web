import os

from flask import Blueprint, request, jsonify, send_from_directory
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

from utils.preprocessing import preprocess_dataframe

predict_bp = Blueprint("predict_bp", __name__)

MODEL_DIR = "models"
DOWNLOAD_DIR = "downloads"


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """Handle file upload and return forecast results."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    model_name = request.form.get('model')
    if not model_name:
        return jsonify({'error': 'No model selected'}), 400

    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        X, dates = preprocess_dataframe(df)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400

    model_path = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        return jsonify({'error': 'Model not found'}), 400

    if model_path.endswith(('.pkl', '.joblib')):
        model = joblib.load(model_path)
        preds = model.predict(X).reshape(-1).tolist()
    elif model_path.endswith('.h5'):
        model = load_model(model_path)
        preds = model.predict(X).reshape(-1).tolist()
    else:
        return jsonify({'error': 'Unsupported model format'}), 400

    # build result frame and save to downloads
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    result_df = pd.DataFrame({"Date": dates, "Predicted": preds})
    result = {
        "dates": dates,
        "predicted": preds,
    }
    if "Value" in df.columns:
        result_df["Actual"] = df["Value"].tolist()
        result["actual"] = df["Value"].tolist()

    csv_path = os.path.join(DOWNLOAD_DIR, "forecast.csv")
    excel_path = os.path.join(DOWNLOAD_DIR, "forecast.xlsx")
    result_df.to_csv(csv_path, index=False)
    result_df.to_excel(excel_path, index=False)

    return jsonify(result)


@predict_bp.route("/upload_model", methods=["POST"])
def upload_model():
    """Upload a model file to the models directory."""
    if "model_file" not in request.files:
        return jsonify({"error": "No model file uploaded"}), 400

    file = request.files["model_file"]
    if file.filename == "":
        return jsonify({"error": "No filename"}), 400

    if not file.filename.endswith((".pkl", ".joblib", ".h5")):
        return jsonify({"error": "Unsupported model format"}), 400

    os.makedirs(MODEL_DIR, exist_ok=True)
    save_path = os.path.join(MODEL_DIR, file.filename)
    file.save(save_path)
    return jsonify({"name": file.filename})


@predict_bp.route("/download/<ftype>")
def download_file(ftype: str):
    """Download forecast results as csv or excel."""
    if ftype == "csv":
        filename = "forecast.csv"
    else:
        filename = "forecast.xlsx"
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
