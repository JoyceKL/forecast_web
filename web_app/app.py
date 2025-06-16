from flask import Flask, render_template

from routes.predict import predict_bp
from utils.model_utils import get_available_models

app = Flask(__name__)
app.register_blueprint(predict_bp)


@app.route('/')
def index():
    models = get_available_models()
    return render_template('index.html', models=models)


if __name__ == '__main__':
    app.run(debug=True)
