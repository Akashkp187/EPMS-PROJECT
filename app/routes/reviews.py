"""
Performance reviews
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from sqlalchemy import or_

from app import db
from app.models import Review, User
from app.utils import manager_required

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/")
@login_required
def index():
    if current_user.is_manager():
        # Show reviews they created or reviews for employees they manage (direct reports + same department)
        managed_ids = [
            u.id for u in User.query.filter(
                or_(User.manager_id == current_user.id, User.department_id == current_user.department_id)
            ).filter(User.id != current_user.id).all()
            if current_user.can_manage_user(u)
        ]
        if managed_ids:
            reviews = (
                Review.query.filter(
                    or_(
                        Review.reviewer_id == current_user.id,
                        Review.user_id.in_(managed_ids),
                    )
                )
                .order_by(Review.created_at.desc())
                .all()
            )
        else:
            reviews = Review.query.filter(Review.reviewer_id == current_user.id).order_by(Review.created_at.desc()).all()
    else:
        reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template("reviews/index.html", reviews=reviews)


@reviews_bp.route("/create", methods=["GET", "POST"])
@manager_required
def create():
    if request.method == "POST":
        user_id = request.form.get("user_id", type=int)
        if not user_id or not current_user.can_manage_user(User.query.get(user_id)):
            flash("Invalid employee.", "error")
            return redirect(url_for("reviews.index"))
        try:
            period_start = datetime.strptime(request.form.get("period_start", ""), "%Y-%m-%d").date()
            period_end = datetime.strptime(request.form.get("period_end", ""), "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid dates.", "error")
            return redirect(url_for("reviews.create"))
        review = Review(
            user_id=user_id,
            reviewer_id=current_user.id,
            period_start=period_start,
            period_end=period_end,
            summary=request.form.get("summary", "").strip() or None,
            status="draft",
        )
        db.session.add(review)
        db.session.commit()
        flash("Review created.", "success")
        return redirect(url_for("reviews.index"))
    reports = current_user.direct_reports.all() if current_user.is_manager() else []
    return render_template("reviews/form.html", review=None, reports=reports)


@reviews_bp.route("/<int:review_id>")
@login_required
def view(review_id):
    review = Review.query.get_or_404(review_id)
    # Reviewee, reviewer, or manager who can manage reviewee can view
    if (review.user_id != current_user.id and review.reviewer_id != current_user.id
            and not current_user.can_manage_user(review.user)):
        abort(403)
    return render_template("reviews/view.html", review=review)


@reviews_bp.route("/<int:review_id>/edit", methods=["GET", "POST"])
@manager_required
def edit(review_id):
    review = Review.query.get_or_404(review_id)
    # Only the reviewer can edit; managers cannot edit their employees' reviews
    if review.reviewer_id != current_user.id:
        abort(403)
    if request.method == "POST":
        review.rating = request.form.get("rating", type=int)
        review.summary = request.form.get("summary", "").strip() or None
        review.strengths = request.form.get("strengths", "").strip() or None
        review.improvements = request.form.get("improvements", "").strip() or None
        review.status = request.form.get("status", "draft")
        if review.status == "submitted":
            review.submitted_at = datetime.utcnow()
        db.session.commit()
        flash("Review updated.", "success")
        return redirect(url_for("reviews.view", review_id=review.id))
    return render_template("reviews/form.html", review=review, reports=[])


@reviews_bp.route("/<int:review_id>/delete", methods=["POST"])
@manager_required
def delete(review_id):
    review = Review.query.get_or_404(review_id)
    # Only the reviewer or admin can delete; managers cannot delete their employees' reviews
    if review.reviewer_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("reviews.index"))
