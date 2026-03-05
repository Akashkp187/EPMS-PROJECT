"""
Recognition and badges
"""
from datetime import datetime

from app import db


class Recognition(db.Model):
    __tablename__ = "recognitions"

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge = db.Column(db.String(60), nullable=True)  # star, excellence, teamwork, innovation
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipient = db.relationship("User", foreign_keys=[recipient_id], backref=db.backref("recognitions_received", lazy="dynamic"))
    sender = db.relationship("User", foreign_keys=[sender_id])
