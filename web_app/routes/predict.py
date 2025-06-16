import os

from flask import Blueprint, request, jsonify
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

from utils.preprocessing import preprocess_dataframe

predict_bp = Blueprint("predict_bp", __name__)


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

    model_path = os.path.join('models', model_name)
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

    result = {
        'dates': dates,
        'predicted': preds,
    }
    if 'Value' in df.columns:
        result['actual'] = df['Value'].tolist()

    return jsonify(result)
