
from flask import Flask, request, jsonify
import pandas as pd
import joblib
from datetime import datetime
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from xgboost import XGBRegressor

app = Flask(__name__)

# Load models
sarimax_model = SARIMAXResults.load("models/sarimax_model.pkl")
xgb_model = joblib.load("models/xgb_model.pkl")

@app.route("/api/forecast", methods=["POST"])
def forecast():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    actual = df["Value"].values.tolist() if "Value" in df.columns else []
    dates = df.index.strftime("%Y-%m-%d").tolist()

    exog = df.drop(columns=["Value"], errors='ignore')
    exog = exog.loc[:, ~exog.columns.duplicated()]

    pred = sarimax_model.predict(start=dates[0], end=dates[-1], exog=exog)

    return jsonify({
        "dates": dates,
        "actual": actual,
        "predicted": pred.tolist()
    })

if __name__ == "__main__":
    app.run(debug=True)
