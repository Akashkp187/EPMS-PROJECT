"""
360-degree feedback model
"""
from datetime import datetime

from app import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    feedback_type = db.Column(db.String(20), default="peer")  # peer, manager, self, subordinate
    rating = db.Column(db.Integer, nullable=True)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default="submitted")  # draft, submitted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recipient = db.relationship("User", foreign_keys=[recipient_id])
    sender = db.relationship("User", foreign_keys=[sender_id])
