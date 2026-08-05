from app.extensions import db
from datetime import datetime

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50), nullable=True) 
    color = db.Column(db.String(50), nullable=True) 
    sku = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    product_variant = db.relationship('ProductVariant', backref='order_items')

    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_variant_id': self.product_variant_id,
            'product_name': self.product_name,
            'size': self.product_variant.size if self.product_variant else None,  
            'color': self.product_variant.color if self.product_variant else None,
            'sku': self.sku,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }