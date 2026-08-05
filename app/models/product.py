from app.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20))
    brand = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2))
    weight = db.Column(db.Numeric(8, 3))
    keywords = db.Column(db.JSON)
    status = db.Column(db.String(20), default='active')
    total_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'description': self.description,
            'category': self.category,
            'sub_category': self.sub_category,
            'gender': self.gender,
            'brand': self.brand,
            'base_price': float(self.base_price) if self.base_price else None,
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'weight': float(self.weight) if self.weight else None,
            'keywords': self.keywords or [],
            'status': self.status,
            'total_quantity': self.total_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'variants': [variant.to_dict() for variant in self.variants]
        }
