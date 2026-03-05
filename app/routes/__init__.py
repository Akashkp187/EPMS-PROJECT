"""
Register all blueprints
"""
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.employees import employees_bp
from app.routes.departments import departments_bp
from app.routes.goals import goals_bp
from app.routes.reviews import reviews_bp
from app.routes.feedback import feedback_bp
from app.routes.training import training_bp
from app.routes.meetings import meetings_bp
from app.routes.kpi import kpi_bp
from app.routes.notifications import notifications_bp
from app.routes.profile import profile_bp
from app.routes.settings import settings_bp
from app.routes.analytics import analytics_bp
from app.routes.api import api_bp
from app.routes.recognition import recognition_bp
from app.routes.performance_support import performance_support_bp
from app.routes.moderate import moderate_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(departments_bp, url_prefix="/departments")
    app.register_blueprint(goals_bp, url_prefix="/goals")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")
    app.register_blueprint(training_bp, url_prefix="/training")
    app.register_blueprint(meetings_bp, url_prefix="/meetings")
    app.register_blueprint(kpi_bp, url_prefix="/kpi")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(recognition_bp, url_prefix="/recognition")
    app.register_blueprint(performance_support_bp, url_prefix="/performance-support")
    app.register_blueprint(moderate_bp, url_prefix="/moderate")
