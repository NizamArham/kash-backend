from app.extensions import db
from datetime import datetime
import pytz

SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    return datetime.now(SL_TIMEZONE)

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    alternative_phone = db.Column(db.String(20))
    dob = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    
    tier = db.Column(db.Enum('bronze', 'silver', 'gold', 'platinum'), default='bronze')
    loyalty_points = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    last_order_date = db.Column(db.Date)
    
    notes = db.Column(db.Text)
    
    # ✅ Soft delete fields
    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    restored_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=get_sl_time)
    updated_at = db.Column(db.DateTime, default=get_sl_time, onupdate=get_sl_time)
    
    # Relationships
    addresses = db.relationship('CustomerAddress', backref='customer', lazy=True, cascade='all, delete-orphan')
    loyalty_transactions = db.relationship('LoyaltyTransaction', backref='customer', lazy=True, cascade='all, delete-orphan')
    deleted_by_employee = db.relationship('Employee', foreign_keys=[deleted_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'phone': self.phone,
            'alternative_phone': self.alternative_phone,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'tier': self.tier,
            'loyalty_points': self.loyalty_points,
            'total_orders': self.total_orders,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by': self.deleted_by,
            'restored_at': self.restored_at.isoformat() if self.restored_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'addresses': [addr.to_dict() for addr in self.addresses]
        }
    
    def update_tier(self):
        """Update customer tier based on loyalty points"""
        if self.loyalty_points >= 2000:
            self.tier = 'platinum'
        elif self.loyalty_points >= 1000:
            self.tier = 'gold'
        elif self.loyalty_points >= 500:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
