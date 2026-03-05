"""
Competency framework
"""
from datetime import datetime

from app import db


class Competency(db.Model):
    __tablename__ = "competencies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee_competencies = db.relationship(
        "EmployeeCompetency", backref="competency", lazy="dynamic", cascade="all, delete-orphan"
    )


class EmployeeCompetency(db.Model):
    __tablename__ = "employee_competencies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey("competencies.id"), nullable=False)
    level = db.Column(db.Integer, default=1)  # 1-5
    assessed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("employee_competencies", lazy="dynamic", cascade="all, delete-orphan"))
