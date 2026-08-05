from app.extensions import db
from datetime import datetime
import pytz

SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    return datetime.now(SL_TIMEZONE)

class SystemAccessLog(db.Model):
    __tablename__ = 'system_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=True)
    
    action = db.Column(db.Enum('login', 'logout', 'login_failed'), nullable=False)
    
    session_id = db.Column(db.String(255))
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text)
    
    status = db.Column(db.Enum('success', 'failed'), nullable=False)
    failure_reason = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=get_sl_time)
    
    # Relationship
    employee = db.relationship('Employee', backref='access_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else 'Unknown',
            'action': self.action,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
