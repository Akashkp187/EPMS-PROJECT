"""
Departments management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Department
from app.utils import admin_required

departments_bp = Blueprint("departments", __name__)


@departments_bp.route("/")
@login_required
def index():
    # Admin sees all departments; employees and managers see only their own department
    if current_user.is_admin():
        departments = Department.query.order_by(Department.name).all()
    else:
        departments = [current_user.department] if current_user.department else []
    return render_template("departments/index.html", departments=departments)


@departments_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip() or None
        description = request.form.get("description", "").strip() or None
        image_url = request.form.get("image_url", "").strip() or None
        if not name:
            flash("Name is required.", "error")
        elif Department.query.filter_by(name=name).first():
            flash("Department with this name already exists.", "error")
        else:
            dept = Department(name=name, code=code, description=description, image_url=image_url)
            db.session.add(dept)
            db.session.commit()
            flash("Department created.", "success")
            return redirect(url_for("departments.index"))
    return render_template("departments/form.html", department=None)


@departments_bp.route("/<int:dept_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(dept_id):
    department = Department.query.get_or_404(dept_id)
    if request.method == "POST":
        department.name = request.form.get("name", "").strip()
        department.code = request.form.get("code", "").strip() or None
        department.description = request.form.get("description", "").strip() or None
        department.image_url = request.form.get("image_url", "").strip() or None
        db.session.commit()
        flash("Department updated.", "success")
        return redirect(url_for("departments.index"))
    return render_template("departments/form.html", department=department)
