"""
360 Feedback
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Feedback, User

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/")
@login_required
def index():
    received = Feedback.query.filter_by(recipient_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    sent = Feedback.query.filter_by(sender_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    return render_template("feedback/index.html", received=received, sent=sent)


@feedback_bp.route("/give", methods=["GET", "POST"])
@login_required
def give():
    if request.method == "POST":
        recipient_id = request.form.get("recipient_id", type=int)
        recipient = User.query.get(recipient_id)
        if not recipient or recipient.id == current_user.id:
            flash("Invalid recipient.", "error")
            return redirect(url_for("feedback.give"))
        feedback = Feedback(
            recipient_id=recipient_id,
            sender_id=current_user.id,
            feedback_type=request.form.get("feedback_type", "peer"),
            rating=request.form.get("rating", type=int),
            comment=request.form.get("comment", "").strip() or None,
            is_anonymous=request.form.get("is_anonymous") == "on",
            status="submitted",
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback submitted.", "success")
        return redirect(url_for("feedback.index"))
    users = User.query.filter(User.id != current_user.id, User.is_active == True).order_by(User.first_name).all()
    return render_template("feedback/give.html", users=users)


@feedback_bp.route("/<int:feedback_id>")
@login_required
def view(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    recipient = User.query.get(feedback.recipient_id)
    can_view = (
        feedback.recipient_id == current_user.id
        or feedback.sender_id == current_user.id
        or current_user.is_admin()
        or (recipient and current_user.can_manage_user(recipient))
    )
    if not can_view:
        abort(403)
    return render_template("feedback/view.html", feedback=feedback)


@feedback_bp.route("/<int:feedback_id>/delete", methods=["POST"])
@login_required
def delete(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    # Only the sender or admin can delete; managers cannot delete their employees' feedback
    if feedback.sender_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted.", "info")
    return redirect(url_for("feedback.index"))
