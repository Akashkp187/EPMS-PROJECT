"""
Top performers (department-wise) — visible to all employees for motivation.
Badges and notifications are synced when the page is viewed.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.models import Department
from app.utils.rankings import (
    get_top_performers_by_department,
    get_overall_top_performers,
    ensure_top_performer_badges,
    ensure_overall_top_performer_badges,
    BADGE_TOP_PERFORMER_TITLE,
    BADGE_OVERALL_TOP_TITLE,
)

recognition_bp = Blueprint("recognition", __name__)


# Period options for top performers: quarter = 3 months, year = 12 months
PERIOD_MONTHS = {"quarter": 3, "year": 12}


@recognition_bp.route("/")
@login_required
def index():
    """
    Top performers page: department-wise top 3. All employees can see.
    Sync badges + notifications for current period when page loads.
    Optional period: quarter (3 months) or year (12 months).
    """
    department_id = request.args.get("department", type=int)
    period_key = request.args.get("period", "quarter")
    months = PERIOD_MONTHS.get(period_key, 3)
    departments = Department.query.order_by(Department.name).all()
    if not current_user.is_admin() and current_user.department_id:
        departments = [d for d in departments if d.id == current_user.department_id]
    ensure_overall_top_performer_badges(top_n=3, months=months)
    ensure_top_performer_badges(department_id=department_id, top_n=3, months=months)
    overall_top_3 = get_overall_top_performers(top_n=3, months=months)
    top_by_dept = get_top_performers_by_department(
        department_id=department_id, top_n=3, months=months
    )
    # Build list of (department, [(user, score), ...]) for template
    dept_list = []
    for dept_id, performers in top_by_dept.items():
        dept = Department.query.get(dept_id)
        if dept and performers:
            dept_list.append((dept, performers))
    return render_template(
        "recognition/index.html",
        overall_top_3=overall_top_3,
        dept_list=dept_list,
        departments=departments,
        selected_department_id=department_id,
        badge_title=BADGE_TOP_PERFORMER_TITLE,
        overall_badge_title=BADGE_OVERALL_TOP_TITLE,
        period=period_key,
    )
