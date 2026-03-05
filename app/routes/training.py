"""
Training management
"""
import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Training, TrainingEnrollment, User, Notification
from app.utils import admin_required, manager_required

training_bp = Blueprint("training", __name__)


def _allowed_training_image(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"})


def _save_training_image(request, training_id):
    """Save uploaded image for training; returns relative URL (e.g. uploads/training/...) or None."""
    if "image" not in request.files:
        return None
    f = request.files["image"]
    if not f or not f.filename or not _allowed_training_image(f.filename):
        return None
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "training"
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = f.filename.rsplit(".", 1)[1].lower()
    filename = f"training_{training_id}_{os.urandom(4).hex()}.{ext}"
    filepath = upload_dir / filename
    f.save(str(filepath))
    return f"uploads/training/{filename}"


@training_bp.route("/")
@login_required
def index():
    from flask_login import current_user
    trainings = Training.query.order_by(Training.start_date.desc()).all()
    my_enrollments = {e.training_id: e for e in TrainingEnrollment.query.filter_by(user_id=current_user.id).all()}
    return render_template("training/index.html", trainings=trainings, my_enrollments=my_enrollments)


@training_bp.route("/assign/<int:user_id>", methods=["GET", "POST"])
@login_required
@manager_required
def assign_user(user_id):
    """Manager (or admin): assign an employee to a training (e.g. for performance support)."""
    target = User.query.get_or_404(user_id)
    if not current_user.can_manage_user(target):
        abort(403)
    trainings = Training.query.filter(Training.status.in_(["scheduled", "in_progress"])).order_by(Training.start_date.desc()).all()
    if request.method == "POST":
        training_id = request.form.get("training_id", type=int)
        if not training_id:
            flash("Please select a training.", "error")
            return redirect(url_for("training.assign_user", user_id=user_id))
        training = Training.query.get_or_404(training_id)
        existing = TrainingEnrollment.query.filter_by(training_id=training_id, user_id=user_id).first()
        if existing and existing.status != "cancelled":
            flash(f"{target.full_name} is already enrolled in this training.", "info")
        else:
            if existing and existing.status == "cancelled":
                existing.status = "enrolled"
                existing.completed_at = None
            else:
                db.session.add(TrainingEnrollment(training_id=training_id, user_id=user_id))
            notif = Notification(
                user_id=user_id,
                title="Training assigned",
                message=f"You have been assigned to \"{training.title}\" by your manager. Please check the Training section.",
                type="info",
                link=url_for("training.view", training_id=training_id),
            )
            db.session.add(notif)
            db.session.commit()
            flash(f"{target.full_name} enrolled in \"{training.title}\". They have been notified.", "success")
        return redirect(url_for("performance_support.index"))
    return render_template("training/assign_user.html", target=target, trainings=trainings)


@training_bp.route("/<int:training_id>")
@login_required
def view(training_id):
    training = Training.query.get_or_404(training_id)
    from flask_login import current_user
    enrollment = TrainingEnrollment.query.filter_by(training_id=training_id, user_id=current_user.id).first()
    return render_template("training/view.html", training=training, enrollment=enrollment)


@training_bp.route("/<int:training_id>/enroll", methods=["POST"])
@login_required
def enroll(training_id):
    from flask_login import current_user
    training = Training.query.get_or_404(training_id)
    existing = TrainingEnrollment.query.filter_by(training_id=training_id, user_id=current_user.id).first()
    if existing and existing.status != "cancelled":
        flash("Already enrolled.", "info")
    else:
        if existing and existing.status == "cancelled":
            existing.status = "enrolled"
            existing.completed_at = None
        else:
            e = TrainingEnrollment(training_id=training_id, user_id=current_user.id)
            db.session.add(e)
        db.session.commit()
        flash("Enrolled successfully.", "success")
    return redirect(url_for("training.view", training_id=training_id))


@training_bp.route("/<int:training_id>/cancel", methods=["POST"])
@login_required
def cancel_enrollment(training_id):
    """Allow any logged-in user (admin, manager, employee) to cancel their own enrollment."""
    from flask_login import current_user

    training = Training.query.get_or_404(training_id)
    enrollment = TrainingEnrollment.query.filter_by(training_id=training_id, user_id=current_user.id).first()
    if not enrollment or enrollment.status == "cancelled":
        flash("No active enrollment to cancel.", "info")
        return redirect(url_for("training.view", training_id=training_id))

    enrollment.status = "cancelled"
    enrollment.completed_at = None
    db.session.commit()
    flash("Training enrollment cancelled.", "info")
    return redirect(url_for("training.view", training_id=training_id))


@training_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    """Admin-only: create a new training program."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip() or None
        provider = request.form.get("provider", "").strip() or None
        duration_hours = request.form.get("duration_hours", type=float)
        status = request.form.get("status", "").strip() or "scheduled"
        start_date_raw = request.form.get("start_date", "").strip()
        end_date_raw = request.form.get("end_date", "").strip()

        if not title:
            flash("Title is required.", "error")
        else:
            start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date() if start_date_raw else None
            end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date() if end_date_raw else None
            t = Training(
                title=title,
                description=description,
                provider=provider,
                duration_hours=duration_hours,
                start_date=start_date,
                end_date=end_date,
                status=status or "scheduled",
            )
            db.session.add(t)
            db.session.flush()
            image_url = _save_training_image(request, t.id)
            if image_url:
                t.image_url = image_url
            db.session.commit()
            flash("Training created.", "success")
            return redirect(url_for("training.index"))
    return render_template("training/form.html", training=None)


@training_bp.route("/<int:training_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(training_id):
    """Admin-only: edit an existing training program."""
    training = Training.query.get_or_404(training_id)
    if request.method == "POST":
        training.title = request.form.get("title", "").strip()
        training.description = request.form.get("description", "").strip() or None
        training.provider = request.form.get("provider", "").strip() or None
        training.duration_hours = request.form.get("duration_hours", type=float)
        training.status = request.form.get("status", "").strip() or training.status

        start_date_raw = request.form.get("start_date", "").strip()
        end_date_raw = request.form.get("end_date", "").strip()
        training.start_date = (
            datetime.strptime(start_date_raw, "%Y-%m-%d").date() if start_date_raw else None
        )
        training.end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date() if end_date_raw else None

        image_url = _save_training_image(request, training.id)
        if image_url:
            training.image_url = image_url

        db.session.commit()
        flash("Training updated.", "success")
        return redirect(url_for("training.view", training_id=training.id))
    return render_template("training/form.html", training=training)
