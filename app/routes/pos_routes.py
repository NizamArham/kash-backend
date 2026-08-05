from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.delivery_partner import DeliveryPartner
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.product_variant import ProductVariant
from app.models.cashier_ledger import CashierLedger
from app.models.courier_cod_ledger import CourierCODLedger
from datetime import datetime
import random

pos_bp = Blueprint('pos', __name__, url_prefix='/api/pos')

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_suffix = str(random.randint(1000, 9999))
    return f"ORD-{timestamp}-{random_suffix}"

@pos_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json
        
        # Validate required fields
        staff_id = data.get('staff_id')
        if not staff_id:
            return jsonify({'success': False, 'error': 'Staff ID is required'}), 400
        
        # Check if staff exists
        staff = Employee.query.get(staff_id)
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404
        
        # Generate order number
        order_number = generate_order_number()
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=data.get('customer_id'),
            staff_id=staff_id,
            order_type=data.get('order_type', 'in-store'),
            order_status='completed',
            payment_method=data.get('payment_method', 'cash'),
            payment_status='paid',
            subtotal=data.get('subtotal', 0),
            discount_total=data.get('discount_total', 0),
            delivery_fee=data.get('delivery_fee', 0),
            total_amount=data.get('total_amount', 0),
            cash_received=data.get('cash_received'),
            change_amount=data.get('change_amount'),
            loyalty_points_used=data.get('loyalty_points_used', 0),
            loyalty_points_earned=data.get('loyalty_points_earned', 0),
            coupon_code=data.get('coupon_code'),
            coupon_discount=data.get('coupon_discount', 0),
            notes=data.get('notes'),
            delivery_partner_id=data.get('delivery_partner_id'),
            shipping_tracking_no=data.get('shipping_tracking_no'),
            delivery_address=data.get('delivery_address'),
            cod_amount=data.get('cod_amount', 0),
            cod_collected=data.get('cod_collected', False)
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in data.get('items', []):
            order_item = OrderItem(
                order_id=order.id,
                product_variant_id=item_data.get('product_variant_id'),
                product_name=item_data.get('product_name'),
                sku=item_data.get('sku'),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                total_price=item_data.get('total_price', 0)
            )
            db.session.add(order_item)
            
            # Update stock
            variant = ProductVariant.query.get(item_data.get('product_variant_id'))
            if variant:
                variant.quantity -= item_data.get('quantity', 1)
        
        # Create cashier ledger entry
        cashier_ledger = CashierLedger(
            cashier_id=staff_id,
            transaction_type='sale',
            reference_id=order_number,
            description=f"Order #{order_number} - Sale",
            debit=order.total_amount if order.payment_method in ['cash', 'full_cod'] else 0,
            credit=0,
            balance=order.total_amount,
            payment_method=order.payment_method,
            payment_details={'order_id': order.id}
        )
        db.session.add(cashier_ledger)
        
        # If COD order, create courier ledger entry
        if order.payment_method == 'full_cod' and order.delivery_partner_id:
            cod_ledger = CourierCODLedger(
                delivery_partner_id=order.delivery_partner_id,
                transaction_type='order_cod',
                reference_id=order_number,
                description=f"COD order #{order_number}",
                debit=order.total_amount,
                credit=0,
                balance=order.total_amount
            )
            db.session.add(cod_ledger)
        
        # Update customer loyalty points
        if order.customer_id:
            customer = Customer.query.get(order.customer_id)
            if customer:
                customer.loyalty_points = (customer.loyalty_points or 0) + order.loyalty_points_earned
                if order.loyalty_points_used > 0:
                    customer.loyalty_points -= order.loyalty_points_used
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')
        order_type = request.args.get('order_type')
        customer_id = request.args.get('customer_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Order.query
        
        if status:
            query = query.filter(Order.order_status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if date_from:
            query = query.filter(Order.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Order.created_at <= datetime.fromisoformat(date_to))
        
        orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # Convert to dict with safe handling
        result = []
        for order in orders.items:
            try:
                result.append(order.to_dict())
            except Exception as e:
                print(f"Error converting order {order.id}: {e}")
                # Fallback to basic dict
                result.append({
                    'id': order.id,
                    'order_number': order.order_number,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'customer_name': 'Error loading customer',
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'items': []
                })
        
        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': orders.page,
                'per_page': orders.per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/orders/simple', methods=['GET'])
def get_orders_simple():
    """Simple endpoint to get orders using model to_dict() methods"""
    try:
        orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
        
        result = []
        for order in orders:
            # Get customer name safely
            customer_name = 'Walk-in Customer'
            customer_phone = None
            customer_email = None
            
            if order.customer:
                try:
                    first = getattr(order.customer, 'first_name', '') or ''
                    last = getattr(order.customer, 'last_name', '') or ''
                    customer_name = f"{first} {last}".strip()
                    if not customer_name:
                        customer_name = 'Walk-in Customer'
                    customer_phone = getattr(order.customer, 'phone', None)
                    customer_email = getattr(order.customer, 'email', None)
                except:
                    pass
            
            # Get staff name safely
            staff_name = ''
            if order.staff:
                try:
                    first = getattr(order.staff, 'first_name', '') or ''
                    last = getattr(order.staff, 'last_name', '') or ''
                    staff_name = f"{first} {last}".strip()
                except:
                    pass
            
            # Get items using the model's to_dict() method
            items = []
            for item in order.items:
                try:
                    items.append(item.to_dict())
                except Exception as e:
                    print(f"Error converting item {item.id}: {e}")
                    # Fallback
                    items.append({
                        'id': item.id,
                        'order_id': item.order_id,
                        'product_variant_id': item.product_variant_id,
                        'product_name': item.product_name,
                        'size': '-',
                        'color': '-',
                        'sku': item.sku,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price) if item.unit_price else 0,
                        'total_price': float(item.total_price) if item.total_price else 0,
                        'created_at': item.created_at.isoformat() if item.created_at else None
                    })
            
            result.append({
                'id': order.id,
                'order_number': order.order_number,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'customer_name': customer_name,
                'customer': {
                    'phone': customer_phone,
                    'email': customer_email
                } if customer_name != 'Walk-in Customer' else None,
                'order_type': order.order_type,
                'order_status': order.order_status,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'subtotal': float(order.subtotal) if order.subtotal else 0,
                'discount_total': float(order.discount_total) if order.discount_total else 0,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'staff_name': staff_name,
                'delivery_address': order.delivery_address,
                'items': items,
                'item_count': len(items)
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
            
        return jsonify({
            'success': True,
            'data': order.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
            
        data = request.json
        new_status = data.get('order_status')
        
        if new_status not in ['pending', 'processing', 'completed', 'cancelled', 'shipped', 'delivered']:
            return jsonify({'success': False, 'error': 'Invalid order status'}), 400
            
        order.order_status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': f'Order status updated to {new_status}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/orders/<int:order_id>/cod-collect', methods=['PUT'])
def collect_cod(order_id):
    """Mark COD as collected"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
            
        if order.payment_method != 'full_cod':
            return jsonify({'success': False, 'error': 'Not a COD order'}), 400
            
        if order.cod_collected:
            return jsonify({'success': False, 'error': 'COD already collected'}), 400
            
        order.cod_collected = True
        order.cod_collected_date = datetime.utcnow()
        
        # Update courier ledger
        if order.delivery_partner_id:
            cod_ledger = CourierCODLedger.query.filter_by(
                delivery_partner_id=order.delivery_partner_id,
                reference_id=order.order_number,
                transaction_type='order_cod'
            ).first()
            
            if cod_ledger:
                cod_ledger.transaction_type = 'payment_received'
                cod_ledger.description = f"COD payment received for {order.order_number}"
                cod_ledger.credit = order.total_amount
                cod_ledger.balance = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': 'COD collected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/delivery-partners', methods=['GET'])
def get_delivery_partners():
    """Get all active delivery partners"""
    try:
        partners = DeliveryPartner.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [partner.to_dict() for partner in partners]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/cashier-ledger', methods=['GET'])
def get_cashier_ledger():
    """Get cashier ledger entries"""
    try:
        cashier_id = request.args.get('cashier_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = CashierLedger.query
        
        if cashier_id:
            query = query.filter(CashierLedger.cashier_id == cashier_id)
        if date_from:
            query = query.filter(CashierLedger.transaction_date >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(CashierLedger.transaction_date <= datetime.fromisoformat(date_to))
        
        entries = query.order_by(CashierLedger.transaction_date.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/courier-ledger', methods=['GET'])
def get_courier_ledger():
    """Get courier COD ledger entries"""
    try:
        partner_id = request.args.get('delivery_partner_id', type=int)
        
        query = CourierCODLedger.query
        
        if partner_id:
            query = query.filter(CourierCODLedger.delivery_partner_id == partner_id)
        
        entries = query.order_by(CourierCODLedger.transaction_date.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pos_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get POS dashboard statistics"""
    try:
        from sqlalchemy import func
        
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        
        # Today's sales
        today_orders = Order.query.filter(
            Order.created_at >= today_start,
            Order.order_status == 'completed'
        ).all()
        
        today_sales = sum(order.total_amount for order in today_orders)
        today_count = len(today_orders)
        
        # Total orders
        total_orders = Order.query.filter_by(order_status='completed').count()
        
        # Total revenue
        total_revenue = db.session.query(
            func.sum(Order.total_amount)
        ).filter_by(order_status='completed').scalar() or 0
        
        # Customer count
        total_customers = Customer.query.filter_by(is_active=True).count()
        
        # Recent orders
        recent_orders = Order.query.filter_by(order_status='completed').order_by(
            Order.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'today_sales': float(today_sales),
                'today_orders': today_count,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'total_customers': total_customers,
                'recent_orders': [order.to_dict() for order in recent_orders]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500