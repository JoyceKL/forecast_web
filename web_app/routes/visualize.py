import os
import pandas as pd
from flask import Blueprint, render_template, send_from_directory

visualize_bp = Blueprint("visualize_bp", __name__)

DOWNLOAD_DIR = "downloads"
CHART_DIR = os.path.join("static", "charts")
CHART_FILE = "forecast.png"


@visualize_bp.route("/visualize")
def visualize_page():
    """Render forecast result page with data previews."""
    train_path = os.path.join(DOWNLOAD_DIR, "train_processed.csv")
    test_path = os.path.join(DOWNLOAD_DIR, "test_processed.csv")
    train_preview, test_preview = [], []
    if os.path.exists(train_path):
        train_preview = pd.read_csv(train_path).head().to_dict(orient="records")
    if os.path.exists(test_path):
        test_preview = pd.read_csv(test_path).head().to_dict(orient="records")
    return render_template(
        "chart_result.html", train_preview=train_preview, test_preview=test_preview
    )


@visualize_bp.route("/visualize/download/<which>")
def download_processed(which: str):
    """Download processed train or test CSV."""
    filename = "train_processed.csv" if which == "train" else "test_processed.csv"
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


@visualize_bp.route("/visualize/download/chart")
def download_chart():
    """Download forecast chart PNG."""
    return send_from_directory(CHART_DIR, CHART_FILE, as_attachment=True)
