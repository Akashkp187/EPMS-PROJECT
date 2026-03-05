"""
User profile
"""
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, Recognition
from app.utils import admin_required, manager_required

profile_bp = Blueprint("profile", __name__)


def allowed_file(filename):
    from flask import current_app
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config.get("ALLOWED_EXTENSIONS", set())


@profile_bp.route("/")
@login_required
def index():
    return redirect(url_for("profile.view", user_id=current_user.id))


@profile_bp.route("/<int:user_id>")
@login_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id and not current_user.can_manage_user(user):
        abort(403)
    recognitions = user.recognitions_received.order_by(Recognition.created_at.desc()).limit(10).all()
    return render_template("profile/view.html", user=user, recognitions=recognitions)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    user = current_user
    if request.method == "POST":
        user.first_name = request.form.get("first_name", "").strip()
        user.last_name = request.form.get("last_name", "").strip()
        user.job_title = request.form.get("job_title", "").strip() or None
        user.phone = request.form.get("phone", "").strip() or None
        if "avatar" in request.files:
            f = request.files["avatar"]
            if f and f.filename and allowed_file(f.filename):
                from flask import current_app
                upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "avatars"
                upload_dir.mkdir(parents=True, exist_ok=True)
                ext = f.filename.rsplit(".", 1)[1].lower()
                filename = f"user_{user.id}_{os.urandom(4).hex()}.{ext}"
                filepath = upload_dir / filename
                f.save(str(filepath))
                user.avatar_url = f"uploads/avatars/{filename}"
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile.view", user_id=user.id))
    return render_template("profile/edit.html", user=user)
