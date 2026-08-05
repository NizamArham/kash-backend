from app.extensions import db
from datetime import datetime
import pytz

SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    return datetime.now(SL_TIMEZONE)

class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    points = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    
    source = db.Column(db.Enum('purchase', 'promotion', 'manual_add', 'redeem', 'expiry'), default='manual_add')
    reference_id = db.Column(db.Integer)
    processed_by = db.Column(db.Integer, db.ForeignKey('employees.id'))
    
    created_at = db.Column(db.DateTime, default=get_sl_time)
    
    # Relationship
    processor = db.relationship('Employee', backref='processed_loyalty')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'points': self.points,
            'balance_after': self.balance_after,
            'reason': self.reason,
            'source': self.source,
            'reference_id': self.reference_id,
            'processed_by': self.processed_by,
            'processed_by_name': f"{self.processor.first_name} {self.processor.last_name}" if self.processor else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
