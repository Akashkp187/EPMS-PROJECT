"""
Goal model for performance goals
"""
from datetime import datetime

from app import db


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="active")  # active, completed, cancelled
    progress = db.Column(db.Integer, default=0)  # 0-100
    weight = db.Column(db.Integer, default=1)  # for ordering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("goals", lazy="dynamic"))

    def __repr__(self):
        return f"<Goal {self.title[:30]}>"
