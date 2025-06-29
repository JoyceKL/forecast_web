import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect
from werkzeug.utils import secure_filename
from utils.model_utils import get_model_details

upload_bp = Blueprint("upload_bp", __name__)

MODEL_DIR = "models"

@upload_bp.route("/upload_model/")
def upload_model_page():
    """Render upload model page with list of existing models."""
    models = get_model_details(MODEL_DIR)
    return render_template("upload_model.html", models=models)


@upload_bp.route("/upload_model/submit", methods=["POST"])
def upload_model():
    """Upload a model file to the models directory."""
    if "model_file" not in request.files:
        return jsonify({"error": "No model file uploaded"}), 400

    file = request.files["model_file"]
    if file.filename == "":
        return jsonify({"error": "No filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pkl", ".h5"}:
        return jsonify({"error": "Unsupported model format"}), 400

    os.makedirs(MODEL_DIR, exist_ok=True)

    base_name = request.form.get("model_name") or os.path.splitext(file.filename)[0]
    base_name = secure_filename(base_name)
    filename = f"{base_name}{ext}"
    save_path = os.path.join(MODEL_DIR, filename)
    counter = 1
    while os.path.exists(save_path):
        filename = f"{base_name}_{counter}{ext}"
        save_path = os.path.join(MODEL_DIR, filename)
        counter += 1

    file.save(save_path)

    # append log
    log_path = os.path.join(MODEL_DIR, "upload.log")
    with open(log_path, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {filename}\n")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"name": filename})
    return redirect("/upload_model/")


@upload_bp.route("/upload_model/delete/<model_name>", methods=["POST"])
def delete_model(model_name: str):
    """Delete a model file from the models directory."""
    safe_name = secure_filename(model_name)
    path = os.path.join(MODEL_DIR, safe_name)
    if os.path.exists(path):
        os.remove(path)
    return redirect("/upload_model/")
