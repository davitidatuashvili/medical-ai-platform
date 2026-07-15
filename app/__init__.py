from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os
db = SQLAlchemy()
login_manager = LoginManager()
metrics = PrometheusMetrics.for_app_factory()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="change-this-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + str(Path(app.instance_path) / "medical_ai.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
        UPLOAD_FOLDER=str(Path(app.root_path) / "static" / "uploads"),
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    metrics.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "გთხოვთ, ჯერ შეხვიდეთ სისტემაში."

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()

    return app
