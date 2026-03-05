"""
Admin-only: moderate and delete any reviews and feedback across the organization.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Review, Feedback, User
from app.utils import admin_required

moderate_bp = Blueprint("moderate", __name__)


@moderate_bp.route("/")
@login_required
@admin_required
def index():
    """List all reviews and all feedback with delete actions (admin only)."""
    reviews = (
        Review.query
        .order_by(Review.created_at.desc())
        .limit(200)
        .all()
    )
    feedback_list = (
        Feedback.query
        .order_by(Feedback.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template(
        "moderate/index.html",
        reviews=reviews,
        feedback_list=feedback_list,
    )


@moderate_bp.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("moderate.index"))


@moderate_bp.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted.", "info")
    return redirect(url_for("moderate.index"))
