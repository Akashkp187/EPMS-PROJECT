"""
1-on-1 Meetings
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Meeting, User
from app.models.user import Role
from app.utils import manager_required

meetings_bp = Blueprint("meetings", __name__)


@meetings_bp.route("/")
@login_required
def index():
    meetings = (
        Meeting.query.filter(
            (Meeting.employee_id == current_user.id) | (Meeting.manager_id == current_user.id),
        )
        .order_by(Meeting.scheduled_at.desc())
        .all()
    )
    return render_template("meetings/index.html", meetings=meetings)


@meetings_bp.route("/create", methods=["GET", "POST"])
@manager_required
def create():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", type=int)
        emp = User.query.get(employee_id)
        if not emp or not current_user.can_manage_user(emp):
            flash("Invalid employee.", "error")
            return redirect(url_for("meetings.create"))
        try:
            scheduled_at = datetime.strptime(
                request.form.get("scheduled_at", "").replace("T", " ")[:16],
                "%Y-%m-%d %H:%M",
            )
        except ValueError:
            flash("Invalid date/time.", "error")
            return redirect(url_for("meetings.create"))
        meeting = Meeting(
            employee_id=employee_id,
            manager_id=current_user.id,
            scheduled_at=scheduled_at,
            duration_minutes=int(request.form.get("duration_minutes", 30) or 30),
            title=request.form.get("title", "").strip() or None,
            agenda=request.form.get("agenda", "").strip() or None,
            status="scheduled",
        )
        db.session.add(meeting)
        db.session.commit()
        flash("Meeting scheduled.", "success")
        return redirect(url_for("meetings.index"))
    # Employees (and managers) this user can manage — for 1:1 scheduling (direct reports + same department)
    assignable = []
    if current_user.is_manager():
        assignable = User.query.filter(User.is_active.is_(True), User.role.in_([Role.EMPLOYEE, Role.MANAGER])).all()
        assignable = [u for u in assignable if current_user.can_manage_user(u) and u.id != current_user.id]
    # Pre-select employee when coming from Performance Support (e.g. ?employee_id=...)
    selected_employee_id = request.args.get("employee_id", type=int)
    if selected_employee_id and not any(u.id == selected_employee_id for u in assignable):
        selected_employee_id = None
    return render_template("meetings/form.html", meeting=None, reports=assignable, selected_employee_id=selected_employee_id)


@meetings_bp.route("/<int:meeting_id>/edit", methods=["GET", "POST"])
@login_required
def edit(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    # Only the manager can edit a 1:1 meeting; employees can view but not edit
    if meeting.manager_id != current_user.id:
        abort(403)
    if request.method == "POST":
        meeting.notes = request.form.get("notes", "").strip() or None
        meeting.status = request.form.get("status", meeting.status)
        try:
            meeting.scheduled_at = datetime.strptime(
                request.form.get("scheduled_at", "").replace("T", " ")[:16],
                "%Y-%m-%d %H:%M",
            )
        except ValueError:
            pass
        meeting.title = request.form.get("title", "").strip() or None
        meeting.agenda = request.form.get("agenda", "").strip() or None
        db.session.commit()
        flash("Meeting updated.", "success")
        return redirect(url_for("meetings.index"))
    return render_template("meetings/form.html", meeting=meeting, reports=[])
