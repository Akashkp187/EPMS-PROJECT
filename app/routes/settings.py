"""
Settings page
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "password":
            current = request.form.get("current_password", "")
            new = request.form.get("new_password", "")
            if not current_user.check_password(current):
                flash("Current password is incorrect.", "error")
            elif len(new) < 8:
                flash("New password must be at least 8 characters.", "error")
            else:
                current_user.set_password(new)
                db.session.commit()
                flash("Password updated.", "success")
        elif action == "theme":
            # Theme can be stored in cookie/localStorage on frontend; optional backend pref
            flash("Preferences saved.", "success")
        return redirect(url_for("settings.index"))
    return render_template("settings/index.html")
