from flask import Flask, render_template

from routes.predict import predict_bp
from routes.upload_model import upload_bp
from routes.preprocess import preprocess_bp
from routes.visualize import visualize_bp
from routes.forecast import forecast_bp
from utils.model_utils import get_available_models, get_history_stats

app = Flask(__name__)
app.register_blueprint(predict_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(preprocess_bp)
app.register_blueprint(visualize_bp)
app.register_blueprint(forecast_bp)


@app.route('/')
def index():
    models = get_available_models()
    stats = get_history_stats()
    stats["model_count"] = len(models)
    return render_template('index.html', models=models, stats=stats)


if __name__ == '__main__':
    app.run(debug=True)
