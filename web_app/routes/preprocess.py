import os
from flask import Blueprint, request, jsonify, send_from_directory, render_template
import pandas as pd
from utils.data_processing import full_pipeline

preprocess_bp = Blueprint("preprocess_bp", __name__)

DOWNLOAD_DIR = "downloads"


@preprocess_bp.route("/preprocess")
def preprocess_page():
    """Render the preprocessing page."""
    return render_template("preprocess.html")


@preprocess_bp.route("/run_preprocess", methods=["POST"])
def run_preprocess():
    """Handle file upload and run preprocessing pipeline."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    use_ssa = request.form.get("ssa") == "on"
    use_wavelet = request.form.get("wavelet") == "on"
    use_rolling = request.form.get("rolling") == "on"
    lag = int(request.form.get("lag", 1))
    split_ratio = float(request.form.get("split_ratio", 0.7))
    split_date = request.form.get("split_date") or None
    scaler = request.form.get("scaler", "minmax")

    try:
        train_df, test_df, stats = full_pipeline(
            df,
            use_ssa=use_ssa,
            use_wavelet=use_wavelet,
            use_rolling=use_rolling,
            lag=lag,
            split_ratio=split_ratio,
            split_date=split_date,
            scaler=scaler,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    train_path = os.path.join(DOWNLOAD_DIR, "train_processed.csv")
    test_path = os.path.join(DOWNLOAD_DIR, "test_processed.csv")
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    result = {
        "train_preview": train_df.head().to_dict(orient="records"),
        "test_preview": test_df.head().to_dict(orient="records"),
        "stats": stats,
    }
    return jsonify(result)


@preprocess_bp.route("/download_processed/<which>")
def download_processed(which: str):
    """Download processed train or test CSV."""
    filename = "train_processed.csv" if which == "train" else "test_processed.csv"
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
