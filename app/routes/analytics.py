"""
Analytics dashboard
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc

from app import db
from app.models import User, Goal, Review, Department, KPITarget

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/")
@login_required
def index():
    # Employees and managers see only their own department; admin can filter by any department
    if current_user.is_admin():
        dept_id = request.args.get("department", type=int)
    else:
        dept_id = current_user.department_id
    period = request.args.get("period", "year")  # quarter, year, all

    # Time window for trend charts
    start_date = None
    if period == "quarter":
        start_date = datetime.utcnow() - timedelta(days=90)
    elif period == "year":
        start_date = datetime.utcnow() - timedelta(days=365)

    # Summary Cards
    employees_query = User.query.filter_by(is_active=True)
    if dept_id:
        employees_query = employees_query.filter(User.department_id == dept_id)
    total_employees = employees_query.count()
    goals_query = Goal.query
    reviews_query = Review.query.filter(Review.status.in_(["submitted", "completed"]))
    if dept_id:
        goals_query = goals_query.join(User, User.id == Goal.user_id).filter(User.department_id == dept_id)
        reviews_query = reviews_query.join(User, User.id == Review.user_id).filter(User.department_id == dept_id)

    total_goals = goals_query.count()
    completed_goals = goals_query.filter(Goal.status == "completed").count()
    reviews_count = reviews_query.count()
    
    # 1. Employee Ranking (Top 5 by Avg Review Rating in period)
    top_employees_query = db.session.query(
        User.first_name,
        User.last_name,
        func.avg(Review.rating).label("avg_rating"),
    ).join(Review, Review.user_id == User.id)
    top_employees_query = top_employees_query.filter(
        Review.rating.isnot(None), User.is_active.is_(True)
    )
    if dept_id:
        top_employees_query = top_employees_query.filter(User.department_id == dept_id)
    if start_date is not None:
        top_employees_query = top_employees_query.filter(Review.period_end >= start_date)
    top_employees_query = (
        top_employees_query.group_by(User.id)
        .order_by(desc("avg_rating"))
        .limit(5)
        .all()
    )
    
    employee_labels = [f"{e.first_name} {e.last_name}" for e in top_employees_query]
    employee_data = [round(e.avg_rating, 1) for e in top_employees_query]

    # 2. Department Performance (Avg Review Rating per Dept in period)
    dept_perf_query = db.session.query(
        Department.name,
        func.avg(Review.rating).label("avg_rating"),
    ).join(User, User.department_id == Department.id).join(
        Review, Review.user_id == User.id
    )
    dept_perf_query = dept_perf_query.filter(Review.rating.isnot(None))
    if start_date is not None:
        dept_perf_query = dept_perf_query.filter(Review.period_end >= start_date)
    dept_perf_query = dept_perf_query.group_by(Department.id).all()
    
    dept_labels = [d.name for d in dept_perf_query]
    dept_data = [round(d.avg_rating, 1) for d in dept_perf_query]

    # 3. Goal Completion Trends (Last periods, grouped by month)
    # Using SQLite strftime for monthly grouping
    goal_trends_query = db.session.query(
        func.strftime('%Y-%m', Goal.updated_at).label("month"),
        func.count(Goal.id),
    ).join(User, User.id == Goal.user_id).filter(Goal.status == "completed")
    if dept_id:
        goal_trends_query = goal_trends_query.filter(User.department_id == dept_id)
    if start_date is not None:
        goal_trends_query = goal_trends_query.filter(Goal.updated_at >= start_date)
    goal_trends_query = (
        goal_trends_query.group_by("month").order_by("month").limit(6).all()
    )
    
    goal_labels = [g.month for g in goal_trends_query]
    goal_data = [g[1] for g in goal_trends_query]

    # 4. KPI Over Time (Avg % Achievement per Period)
    # Achievement = actual / target * 100
    kpi_trend_query = db.session.query(
        KPITarget.period_end,
        func.avg((KPITarget.actual_value / KPITarget.target_value) * 100).label(
            "avg_achievement"
        ),
    ).join(User, User.id == KPITarget.user_id).filter(
        KPITarget.actual_value.isnot(None), KPITarget.target_value > 0
    )
    if dept_id:
        kpi_trend_query = kpi_trend_query.filter(User.department_id == dept_id)
    if start_date is not None:
        kpi_trend_query = kpi_trend_query.filter(KPITarget.period_end >= start_date)
    kpi_trend_query = (
        kpi_trend_query.group_by(KPITarget.period_end)
        .order_by(KPITarget.period_end)
        .limit(6)
        .all()
    )
    
    kpi_labels = [k.period_end.strftime('%b %Y') for k in kpi_trend_query]
    kpi_data = [round(k.avg_achievement, 1) for k in kpi_trend_query]

    # Non-admin only see their own department in the filter
    if current_user.is_admin():
        departments = Department.query.order_by(Department.name).all()
    else:
        departments = [current_user.department] if current_user.department else []
    selected_department = Department.query.get(dept_id) if dept_id else None
    
    return render_template(
        "analytics/index.html",
        total_employees=total_employees,
        total_goals=total_goals,
        completed_goals=completed_goals,
        reviews_count=reviews_count,
        departments=departments,
        selected_department_id=selected_department.id if selected_department else None,
        selected_period=period,
        # Charts Data
        employee_labels=employee_labels,
        employee_data=employee_data,
        dept_labels=dept_labels,
        dept_data=dept_data,
        goal_labels=goal_labels,
        goal_data=goal_data,
        kpi_labels=kpi_labels,
        kpi_data=kpi_data
    )
