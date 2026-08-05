from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    order_type = db.Column(db.Enum('in-store', 'online'), default='in-store')
    order_status = db.Column(db.Enum('pending', 'processing', 'completed', 'cancelled', 'shipped', 'delivered'), default='pending')
    payment_method = db.Column(db.Enum('cash', 'card', 'bank_transfer', 'full_online', 'products_online', 'delivery_online', 'full_cod'), default='cash')
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount_total = db.Column(db.Numeric(10, 2), default=0)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    cash_received = db.Column(db.Numeric(10, 2), nullable=True)
    change_amount = db.Column(db.Numeric(10, 2), nullable=True)
    
    loyalty_points_used = db.Column(db.Integer, default=0)
    loyalty_points_earned = db.Column(db.Integer, default=0)
    
    coupon_code = db.Column(db.String(50), nullable=True)
    coupon_discount = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text, nullable=True)
    
    delivery_partner_id = db.Column(db.Integer, db.ForeignKey('delivery_partners.id'), nullable=True)
    shipping_tracking_no = db.Column(db.String(100), nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    cod_amount = db.Column(db.Numeric(10, 2), default=0)
    cod_collected = db.Column(db.Boolean, default=False)
    cod_collected_date = db.Column(db.DateTime, nullable=True)
    courier_payment_id = db.Column(db.Integer, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    customer = db.relationship('Customer', backref='orders')
    staff = db.relationship('Employee', backref='orders')
    delivery_partner = db.relationship('DeliveryPartner', backref='orders')
    
    def to_dict(self):
        """Convert order to dictionary with safe property access"""
        # Safely get customer name
        customer_name = 'Walk-in Customer'
        customer_data = None
        if self.customer:
            try:
                first = getattr(self.customer, 'first_name', '') or ''
                last = getattr(self.customer, 'last_name', '') or ''
                customer_name = f"{first} {last}".strip()
                if not customer_name:
                    customer_name = 'Walk-in Customer'
                
                customer_data = {
                    'phone': getattr(self.customer, 'phone', None),
                    'email': getattr(self.customer, 'email', None)
                }
            except:
                pass
        
        # Safely get staff name
        staff_name = ''
        if self.staff:
            try:
                first = getattr(self.staff, 'first_name', '') or ''
                last = getattr(self.staff, 'last_name', '') or ''
                staff_name = f"{first} {last}".strip()
            except:
                pass
        
        # Safely get delivery partner name
        partner_name = None
        if self.delivery_partner:
            try:
                partner_name = getattr(self.delivery_partner, 'name', None)
            except:
                pass
        
        # Safely get items
        items_data = []
        if self.items:
            for item in self.items:
                try:
                    items_data.append(item.to_dict())
                except:
                    continue
        
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': customer_name,
            'customer': customer_data,
            'staff_id': self.staff_id,
            'staff_name': staff_name,
            'order_type': self.order_type,
            'order_status': self.order_status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'discount_total': float(self.discount_total) if self.discount_total else 0,
            'delivery_fee': float(self.delivery_fee) if self.delivery_fee else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'cash_received': float(self.cash_received) if self.cash_received else None,
            'change_amount': float(self.change_amount) if self.change_amount else None,
            'loyalty_points_used': self.loyalty_points_used or 0,
            'loyalty_points_earned': self.loyalty_points_earned or 0,
            'coupon_code': self.coupon_code,
            'coupon_discount': float(self.coupon_discount) if self.coupon_discount else 0,
            'notes': self.notes,
            'delivery_partner_id': self.delivery_partner_id,
            'delivery_partner_name': partner_name,
            'shipping_tracking_no': self.shipping_tracking_no,
            'delivery_address': self.delivery_address,
            'cod_amount': float(self.cod_amount) if self.cod_amount else 0,
            'cod_collected': self.cod_collected or False,
            'cod_collected_date': self.cod_collected_date.isoformat() if self.cod_collected_date else None,
            'items': items_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }