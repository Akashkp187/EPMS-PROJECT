"""
Notification model
"""
from datetime import datetime

from app import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(40), default="info")  # info, success, warning, review, recognition
    link = db.Column(db.String(256), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("notifications", lazy="dynamic", order_by="Notification.created_at.desc()"))

    def __repr__(self):
        return f"<Notification {self.title[:30]}>"
