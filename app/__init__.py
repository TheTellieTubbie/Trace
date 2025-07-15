from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .routes import main
from .auth import auth
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "data"), exist_ok=True)

    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app
