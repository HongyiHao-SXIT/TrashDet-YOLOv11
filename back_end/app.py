import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)


    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from models.user import User
    from models.detection import Detection

    # user_loader must be inside create_app (after model import)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    from routes.auth import auth_bp
    from routes.detect import detect_bp
    from routes.dashboard import dashboard_bp
    from routes.map import map_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(map_bp)

    # create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
