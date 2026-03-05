"""
User and Role models with authentication
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from flask_login import UserMixin


class Role:
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    avatar_url = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), nullable=False, default=Role.EMPLOYEE)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(24), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    department = db.relationship("Department", foreign_keys=[department_id], backref=db.backref("members", lazy="dynamic"))
    manager = db.relationship("User", remote_side=[id], backref=db.backref("direct_reports", lazy="dynamic"))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_manager(self):
        return self.role in (Role.ADMIN, Role.MANAGER)

    def can_manage_user(self, other):
        """Return True if this user can manage `other` (for goals, reviews, etc.)."""
        if other is None:
            return False
        if self.is_admin():
            return True
        if self.role == Role.MANAGER:
            # Direct report
            if other.manager_id == self.id:
                return True
            # Anyone in the same department
            if self.department_id is not None and other.department_id == self.department_id:
                return True
        return False

    def __repr__(self):
        return f"<User {self.username}>"
