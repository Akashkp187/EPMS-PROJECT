"""
Dashboard routes
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import Goal, Review, Notification, Meeting, Recognition
from app.utils.performance import compute_user_performance_series

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("dashboard.home"))


@dashboard_bp.route("/home")
@login_required
def home():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.weight, Goal.target_date).limit(5).all()
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).limit(3).all()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).limit(5).all()
    meetings = (
        Meeting.query.filter(
            (Meeting.employee_id == current_user.id) | (Meeting.manager_id == current_user.id),
            Meeting.status == "scheduled",
        )
        .order_by(Meeting.scheduled_at.asc())
        .limit(5)
        .all()
    )

    # High-performer badge: performance above threshold for the last N months
    HIGH_PERF_THRESHOLD = 80.0  # percent
    HIGH_PERF_MIN_MONTHS = 3
    trend_start = datetime.utcnow() - timedelta(days=365)
    perf_series = compute_user_performance_series(
        user_id=current_user.id,
        start_date=trend_start,
        end_date=None,
        max_points=12,
    )
    is_high_performer = False
    if perf_series:
        # Look at the last N points (most recent months)
        recent = perf_series[-HIGH_PERF_MIN_MONTHS :]
        if len(recent) >= HIGH_PERF_MIN_MONTHS:
            scores = [score for _, score in recent]
            if scores and min(scores) >= HIGH_PERF_THRESHOLD:
                is_high_performer = True
                # Reward: create a recognition + notification if not already granted
                existing_recognition = Recognition.query.filter_by(
                    recipient_id=current_user.id, badge="high_performer"
                ).first()
                if existing_recognition is None:
                    recognition = Recognition(
                        recipient_id=current_user.id,
                        sender_id=current_user.id,
                        badge="high_performer",
                        message="Consistently strong goals, reviews, and KPI performance.",
                    )
                    db.session.add(recognition)
                    notification = Notification(
                        user_id=current_user.id,
                        title="High Performer Award",
                        message=(
                            "Congratulations! Based on your recent goals, reviews, and KPI results, "
                            "you've been recognized as a high performer. Please speak with your manager "
                            "about your recognition and any related rewards or bonus."
                        ),
                        type="recognition",
                    )
                    db.session.add(notification)
                    db.session.commit()
    return render_template(
        "dashboard/home.html",
        goals=goals,
        reviews=reviews,
        notifications=notifications,
        meetings=meetings,
        is_high_performer=is_high_performer,
    )
