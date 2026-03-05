"""
Performance support: low performers by department with actions to schedule 1:1 and assign training.
Manager-only (and admin).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Department
from app.utils import manager_required
from app.utils.rankings import get_low_performers_by_department

performance_support_bp = Blueprint("performance_support", __name__)


@performance_support_bp.route("/")
@login_required
@manager_required
def index():
    """
    List low performers by department. Managers see their department(s); admin sees all.
    Each row: employee, score, link to Schedule 1:1, link to Assign training.
    """
    department_id = request.args.get("department", type=int)
    departments = Department.query.order_by(Department.name).all()
    if not current_user.is_admin() and current_user.department_id:
        departments = [d for d in departments if d.id == current_user.department_id]
    low_by_dept = get_low_performers_by_department(
        department_id=department_id,
        bottom_n=5,
        max_score_below=50.0,
    )
    dept_list = []
    for dept_id, performers in low_by_dept.items():
        dept = Department.query.get(dept_id)
        if not dept:
            continue
        # Filter to only employees this manager can manage
        allowed = [
            (u, s) for u, s in performers
            if current_user.can_manage_user(u)
        ]
        if allowed:
            dept_list.append((dept, allowed))
    return render_template(
        "performance_support/index.html",
        dept_list=dept_list,
        departments=departments,
        selected_department_id=department_id,
    )
