"""
KPI management
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.models import KPI, KPITarget, Department
from app.utils import admin_required

kpi_bp = Blueprint("kpi", __name__)


@kpi_bp.route("/")
@login_required
def index():
    kpis = KPI.query.order_by(KPI.name).all()
    return render_template("kpi/index.html", kpis=kpis)


@kpi_bp.route("/targets")
@login_required
def targets():
    from flask_login import current_user
    targets_list = KPITarget.query.filter_by(user_id=current_user.id).order_by(KPITarget.period_end.desc()).all()
    return render_template("kpi/targets.html", targets=targets_list)


@kpi_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    if request.method == "POST":
        kpi = KPI(
            name=request.form.get("name", "").strip(),
            description=request.form.get("description", "").strip() or None,
            unit=request.form.get("unit", "").strip() or None,
            department_id=request.form.get("department_id", type=int) or None,
        )
        db.session.add(kpi)
        db.session.commit()
        flash("KPI created.", "success")
        return redirect(url_for("kpi.index"))
    departments = Department.query.order_by(Department.name).all()
    return render_template("kpi/form.html", kpi=None, departments=departments)
