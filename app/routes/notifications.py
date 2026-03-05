"""
Notifications center
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/")
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    # Mark as read
    for n in notifications:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    return render_template("notifications/index.html", notifications=notifications)


@notifications_bp.route("/<int:nid>/read", methods=["POST"])
@login_required
def mark_read(nid):
    n = Notification.query.filter_by(id=nid, user_id=current_user.id).first()
    if n:
        n.is_read = True
        db.session.commit()
    return redirect(url_for("notifications.index"))
