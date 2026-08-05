from app.extensions import db
from datetime import datetime
import hashlib
import secrets
import pytz

# Sri Lanka Timezone
SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    """Return current Sri Lanka time"""
    return datetime.now(SL_TIMEZONE)

class SystemAccess(db.Model):
    __tablename__ = 'system_access'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    
    role = db.Column(db.Enum('admin', 'manager', 'cashier'), default='cashier', nullable=False)
    
    # ✅ Use SL timezone for timestamps
    last_login_at = db.Column(db.DateTime, default=get_sl_time)
    last_logout_at = db.Column(db.DateTime, default=get_sl_time)
    current_session_id = db.Column(db.String(255))
    
    failed_attempts = db.Column(db.Integer, default=0)
    last_failed_attempt = db.Column(db.DateTime, default=get_sl_time)
    
    is_active = db.Column(db.Boolean, default=True)
    
    # ✅ Use SL timezone for created/updated
    created_at = db.Column(db.DateTime, default=get_sl_time)
    updated_at = db.Column(db.DateTime, default=get_sl_time, onupdate=get_sl_time)
    
    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        password_salt = password + salt
        password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
        return password_hash, salt
    
    @staticmethod
    def verify_password(password, stored_hash, stored_salt):
        password_salt = password + stored_salt
        computed_hash = hashlib.sha256(password_salt.encode()).hexdigest()
        return computed_hash == stored_hash
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'username': self.username,
            'role': self.role,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_logout_at': self.last_logout_at.isoformat() if self.last_logout_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
