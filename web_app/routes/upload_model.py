from flask import Blueprint, request, jsonify
import os

upload_bp = Blueprint("upload_bp", __name__)

MODEL_DIR = "models"


@upload_bp.route("/upload_model", methods=["POST"])
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
