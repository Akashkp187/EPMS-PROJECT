"""
Skills and employee skills (skills matrix)
"""
from datetime import datetime

from app import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    category = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee_skills = db.relationship("EmployeeSkill", backref="skill", lazy="dynamic", cascade="all, delete-orphan")


class EmployeeSkill(db.Model):
    __tablename__ = "employee_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    level = db.Column(db.Integer, default=1)  # 1-5
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("employee_skills", lazy="dynamic", cascade="all, delete-orphan"))
