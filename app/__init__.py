from flask import Flask
from .routes import main
import os

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
    app.secret_key = 'supersecretkey'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.register_blueprint(main)

    return app
