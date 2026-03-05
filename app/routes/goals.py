"""
Goals CRUD
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Goal, User
from app.utils import manager_required

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/")
@login_required
def index():
    user_id = request.args.get("user_id", type=int) or current_user.id
    if user_id != current_user.id and not current_user.can_manage_user(User.query.get(user_id) or current_user):
        abort(403)
    goals = Goal.query.filter_by(user_id=user_id).order_by(Goal.weight, Goal.target_date).all()
    target_user = User.query.get(user_id)
    return render_template("goals/index.html", goals=goals, target_user_id=user_id, target_user=target_user)


@goals_bp.route("/create", methods=["GET", "POST"])
@login_required
@manager_required
def create():
    user_id = request.args.get("user_id", type=int) or current_user.id
    target_user = User.query.get_or_404(user_id)
    if not current_user.can_manage_user(target_user):
        abort(403)
    if request.method == "POST":
        goal = Goal(
            user_id=user_id,
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip() or None,
            status="active",
            progress=int(request.form.get("progress", 0) or 0),
        )
        raw_date = request.form.get("target_date")
        if raw_date:
            try:
                goal.target_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        db.session.add(goal)
        db.session.commit()
        flash("Goal created.", "success")
        return redirect(url_for("goals.index", user_id=user_id))
    return render_template("goals/form.html", goal=None, target_user_id=user_id, target_user=target_user)


@goals_bp.route("/<int:goal_id>/edit", methods=["GET", "POST"])
@login_required
@manager_required
def edit(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if not current_user.can_manage_user(goal.user):
        abort(403)
    if request.method == "POST":
        goal.title = request.form.get("title", "").strip()
        goal.description = request.form.get("description", "").strip() or None
        goal.progress = int(request.form.get("progress", 0) or 0)
        goal.status = request.form.get("status", "active")
        raw_date = request.form.get("target_date")
        if raw_date:
            try:
                goal.target_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        db.session.commit()
        flash("Goal updated.", "success")
        return redirect(url_for("goals.index", user_id=goal.user_id))
    return render_template("goals/form.html", goal=goal, target_user_id=goal.user_id, target_user=goal.user)


@goals_bp.route("/<int:goal_id>/delete", methods=["POST"])
@login_required
@manager_required
def delete(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if not current_user.can_manage_user(goal.user):
        abort(403)
    user_id = goal.user_id
    db.session.delete(goal)
    db.session.commit()
    flash("Goal deleted.", "info")
    return redirect(url_for("goals.index", user_id=user_id))
