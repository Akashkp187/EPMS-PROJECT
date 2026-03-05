"""
Training and enrollments
"""
from datetime import datetime

from app import db


class Training(db.Model):
    __tablename__ = "trainings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)  # uploads/training/... or external URL
    provider = db.Column(db.String(120), nullable=True)
    duration_hours = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="scheduled")  # scheduled, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = db.relationship("TrainingEnrollment", backref="training", lazy="dynamic", cascade="all, delete-orphan")


class TrainingEnrollment(db.Model):
    __tablename__ = "training_enrollments"

    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey("trainings.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="enrolled")  # enrolled, completed, cancelled
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("training_enrollments", lazy="dynamic"))
