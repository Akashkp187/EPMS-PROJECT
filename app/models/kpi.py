"""
KPI and KPI target models
"""
from datetime import datetime

from app import db


class KPI(db.Model):
    __tablename__ = "kpis"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    unit = db.Column(db.String(40), nullable=True)  # %, count, currency
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship("Department", backref=db.backref("kpis", lazy="dynamic"))
    targets = db.relationship("KPITarget", backref="kpi", lazy="dynamic", cascade="all, delete-orphan")


class KPITarget(db.Model):
    __tablename__ = "kpi_targets"

    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey("kpis.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    actual_value = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("kpi_targets", lazy="dynamic"))
