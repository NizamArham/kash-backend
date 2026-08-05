from app.extensions import db
from datetime import datetime

class CourierCODLedger(db.Model):
    __tablename__ = 'courier_cod_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_partner_id = db.Column(db.Integer, db.ForeignKey('delivery_partners.id'), nullable=False)
    transaction_type = db.Column(db.Enum('order_cod', 'payment_received', 'adjustment'), nullable=False)
    reference_id = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    debit = db.Column(db.Numeric(10, 2), default=0)
    credit = db.Column(db.Numeric(10, 2), default=0)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    delivery_partner = db.relationship('DeliveryPartner', backref='cod_ledger')
    
    def to_dict(self):
        return {
            'id': self.id,
            'delivery_partner_id': self.delivery_partner_id,
            'transaction_type': self.transaction_type,
            'reference_id': self.reference_id,
            'description': self.description,
            'debit': float(self.debit),
            'credit': float(self.credit),
            'balance': float(self.balance),
            'transaction_date': self.transaction_date.isoformat()
        }