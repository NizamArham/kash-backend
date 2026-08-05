from app.extensions import db
from datetime import datetime
import pytz

SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    return datetime.now(SL_TIMEZONE)

class CustomerAddress(db.Model):
    __tablename__ = 'customer_addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    type = db.Column(db.Enum('home', 'office', 'other'), default='home')
    is_default = db.Column(db.Boolean, default=False)
    
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=get_sl_time)
    updated_at = db.Column(db.DateTime, default=get_sl_time, onupdate=get_sl_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'is_default': self.is_default,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'postal_code': self.postal_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
