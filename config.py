"""
EPMS Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "epms-dev-secret-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'instance' / 'epms.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Reduce SQLite disk I/O and lock errors (timeout seconds, WAL mode)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 20},
        "pool_pre_ping": True,
    }
    UPLOAD_FOLDER = str(BASE_DIR / "app" / "static" / "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    PAGINATION_PER_PAGE = 12


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


config_by_name = {"development": DevelopmentConfig, "production": ProductionConfig}
