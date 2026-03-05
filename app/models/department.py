"""
Department model
"""
from app import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=True, unique=True)
    description = db.Column(db.Text, nullable=True)
    # Public image URL for department card visuals (Unsplash, CDN, etc.)
    image_url = db.Column(db.String(255), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    head = db.relationship("User", foreign_keys=[head_id], backref=db.backref("headed_departments", lazy="dynamic"))

    def __repr__(self):
        return f"<Department {self.name}>"
