"""
REST API for dashboard data, export, search
"""
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import User, Goal, Review, Notification, KPI, KPITarget
from app.utils.performance import compute_user_performance_series

api_bp = Blueprint("api", __name__)


@api_bp.route("/dashboard/stats")
@login_required
def dashboard_stats():
    """Basic counters for the dashboard header and nav badge."""
    goals = Goal.query.filter_by(user_id=current_user.id)
    total = goals.count()
    completed = goals.filter_by(status="completed").count()
    active = goals.filter_by(status="active").count()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify(
        {
            "goals_total": total,
            "goals_completed": completed,
            "goals_active": active,
            "notifications_unread": unread,
        }
    )


@api_bp.route("/dashboard/goal-completion")
@login_required
def dashboard_goal_completion():
    """
    Goal completion breakdown for the current user.

    Returns labels + counts for goal statuses and an overall completion rate.
    """
    rows = (
        db.session.query(Goal.status, func.count(Goal.id))
        .filter(Goal.user_id == current_user.id)
        .group_by(Goal.status)
        .all()
    )

    status_counts = {status: count for status, count in rows}
    completed = status_counts.get("completed", 0)
    active = status_counts.get("active", 0)
    cancelled = status_counts.get("cancelled", 0)
    total = completed + active + cancelled
    completion_rate = (completed / total * 100.0) if total > 0 else 0.0

    return jsonify(
        {
            "labels": ["Completed", "Active", "Cancelled"],
            "counts": [completed, active, cancelled],
            "completion_rate": round(completion_rate, 1),
            "total_goals": total,
        }
    )


@api_bp.route("/dashboard/rating-distribution")
@login_required
def dashboard_rating_distribution():
    """
    Distribution of review ratings (1–5) for the current user.
    """
    # Count ratings grouped by value
    rows = (
        db.session.query(Review.rating, func.count(Review.id))
        .filter(
            Review.user_id == current_user.id,
            Review.rating.isnot(None),
        )
        .group_by(Review.rating)
        .all()
    )

    distribution = {i: 0 for i in range(1, 6)}
    for rating, count in rows:
        if rating in distribution:
            distribution[rating] = count

    # Average rating for summary
    avg_rating = (
        db.session.query(func.avg(Review.rating))
        .filter(
            Review.user_id == current_user.id,
            Review.rating.isnot(None),
        )
        .scalar()
    )

    return jsonify(
        {
            "labels": [str(i) for i in range(1, 6)],
            "counts": [distribution[i] for i in range(1, 6)],
            "average_rating": round(avg_rating, 1) if avg_rating is not None else None,
        }
    )


@api_bp.route("/dashboard/kpi-progress")
@login_required
def dashboard_kpi_progress():
    """
    KPI achievement comparison for the current user across KPIs.

    For each KPI, we compute avg(actual / target * 100) over that user's targets.
    """
    rows = (
        db.session.query(
            KPI.name,
            func.avg((KPITarget.actual_value / KPITarget.target_value) * 100.0).label(
                "achievement"
            ),
        )
        .join(KPITarget, KPITarget.kpi_id == KPI.id)
        .filter(
            KPITarget.user_id == current_user.id,
            KPITarget.actual_value.isnot(None),
            KPITarget.target_value > 0,
        )
        .group_by(KPI.id)
        .order_by(KPI.name)
        .all()
    )

    labels = [name for name, _ in rows]
    values = [round(achievement, 1) for _, achievement in rows]

    return jsonify(
        {
            "labels": labels,
            "values": values,
        }
    )


@api_bp.route("/dashboard/performance-trend")
@login_required
def dashboard_performance_trend():
    """
    Composite performance trend for the current user.

    Combines goals, reviews, ratings, and KPI achievement into a 0–100
    score per month, using the same formula as our analytics helpers.
    """
    period = request.args.get("period", "year")  # quarter, year, all

    start_date = None
    if period == "quarter":
        start_date = datetime.utcnow() - timedelta(days=90)
    elif period == "year":
        start_date = datetime.utcnow() - timedelta(days=365)

    series = compute_user_performance_series(
        user_id=current_user.id,
        start_date=start_date,
        end_date=None,
        max_points=12,
    )

    labels = [label for label, _ in series]
    values = [score for _, score in series]

    return jsonify({"labels": labels, "values": values})


@api_bp.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()[:100]
    if len(q) < 2:
        return jsonify({"results": []})
    users = (
        User.query.filter(
            User.is_active.is_(True),
            db.or_(
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
            ),
        )
        .limit(10)
        .all()
    )
    return jsonify(
        {
            "results": [
                {
                    "id": u.id,
                    "name": u.full_name,
                    "email": u.email,
                    "url": f"/employees/{u.id}",
                }
                for u in users
            ],
        }
    )
