"""
EPMS Application Factory
"""
import os
from pathlib import Path

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def _ensure_training_image_url_column(app):
    """Add trainings.image_url column if missing (e.g. DB created before column was added)."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    if "sqlite" not in uri:
        return
    try:
        with app.app_context():
            from sqlalchemy import text
            with db.engine.begin() as conn:
                result = conn.execute(text("PRAGMA table_info(trainings)"))
                columns = [row[1] for row in result]
                if "image_url" not in columns:
                    conn.execute(text("ALTER TABLE trainings ADD COLUMN image_url VARCHAR(512)"))
    except Exception:
        pass


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_by_name[config_name])

    # Ensure instance and upload folders exist
    instance_path = app.instance_path
    Path(instance_path).mkdir(parents=True, exist_ok=True)
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)
    (upload_path / "avatars").mkdir(exist_ok=True)
    (upload_path / "training").mkdir(exist_ok=True)

    db.init_app(app)

    # SQLite: enable WAL mode to reduce disk I/O errors
    if "sqlite" in (app.config.get("SQLALCHEMY_DATABASE_URI") or ""):
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=20000")
            cursor.close()

    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)
        _ensure_training_image_url_column(app)

    @app.context_processor
    def inject_overall_top_3():
        """Inject overall_top_3_ids so templates can show org-top avatar ring everywhere."""
        try:
            from app.utils.rankings import get_overall_top_performers
            top = get_overall_top_performers(top_n=3)
            return {"overall_top_3_ids": [u.id for u, _ in top]}
        except Exception:
            return {"overall_top_3_ids": []}

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):  # pragma: no cover - simple view wrapper
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):  # pragma: no cover - simple view wrapper
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):  # pragma: no cover - simple view wrapper
        # In a real app you might log `error` here.
        return render_template("errors/500.html"), 500

    return app
