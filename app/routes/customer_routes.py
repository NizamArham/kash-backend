from flask import Blueprint, request, jsonify
from app.models import Customer, CustomerAddress, LoyaltyTransaction, Employee
from app.extensions import db
from datetime import datetime
import pytz

customer_bp = Blueprint('customer', __name__, url_prefix='/api/customers')

SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    return datetime.now(SL_TIMEZONE)

# ============================================================
# CORS HELPER - Adds CORS headers to all responses
# ============================================================
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# ============================================================
# GET ALL ACTIVE CUSTOMERS
# ============================================================
@customer_bp.route('', methods=['OPTIONS', 'GET'])
def get_customers():
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.created_at.desc()).all()
        response = jsonify({
            'success': True,
            'data': [c.to_dict() for c in customers],
            'count': len(customers)
        })
        return add_cors_headers(response), 200
    except Exception as e:
        print('Error fetching customers:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# GET DELETED CUSTOMERS (Admin Only - View Soft Deleted)
# ============================================================
@customer_bp.route('/deleted', methods=['OPTIONS', 'GET'])
def get_deleted_customers():
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customers = Customer.query.filter_by(is_active=False).order_by(Customer.deleted_at.desc()).all()
        response = jsonify({
            'success': True,
            'data': [c.to_dict() for c in customers],
            'count': len(customers)
        })
        return add_cors_headers(response), 200
    except Exception as e:
        print('Error fetching deleted customers:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# RESTORE DELETED CUSTOMER
# ============================================================
@customer_bp.route('/<int:customer_id>/restore', methods=['OPTIONS', 'PUT'])
def restore_customer(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        if customer.is_active:
            response = jsonify({'success': False, 'error': 'Customer is already active'})
            return add_cors_headers(response), 400
        
        # Restore the customer
        customer.is_active = True
        customer.deleted_at = None
        customer.deleted_by = None
        customer.restored_at = get_sl_time()
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer restored successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error restoring customer:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# CREATE CUSTOMER
# ============================================================
@customer_bp.route('', methods=['OPTIONS', 'POST'])
def create_customer():
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        data = request.json
        
        # Check if email exists
        if data.get('email'):
            existing = Customer.query.filter_by(email=data['email']).first()
            if existing:
                response = jsonify({'success': False, 'error': 'Email already exists'})
                return add_cors_headers(response), 400
        
        # Check if phone exists
        existing = Customer.query.filter_by(phone=data['phone']).first()
        if existing:
            response = jsonify({'success': False, 'error': 'Phone number already exists'})
            return add_cors_headers(response), 400
        
        # Create customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data['phone'],
            alternative_phone=data.get('alternative_phone'),
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date() if data.get('dob') else None,
            gender=data.get('gender'),
            notes=data.get('notes'),
            is_active=True
        )
        
        db.session.add(customer)
        db.session.flush()
        
        # Add addresses
        for addr_data in data.get('addresses', []):
            address = CustomerAddress(
                customer_id=customer.id,
                type=addr_data.get('type', 'home'),
                is_default=addr_data.get('is_default', False),
                address_line1=addr_data['address_line1'],
                address_line2=addr_data.get('address_line2'),
                city=addr_data['city'],
                postal_code=addr_data.get('postal_code')
            )
            db.session.add(address)
            
            # If this is the first address, make it default
            if len(customer.addresses) == 0:
                address.is_default = True
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer created successfully'
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        db.session.rollback()
        print('Error creating customer:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# GET SINGLE CUSTOMER
# ============================================================
@customer_bp.route('/<int:customer_id>', methods=['OPTIONS', 'GET'])
def get_customer(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        response = jsonify({
            'success': True,
            'data': customer.to_dict()
        })
        return add_cors_headers(response), 200
    except Exception as e:
        print('Error fetching customer:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# UPDATE CUSTOMER
# ============================================================
@customer_bp.route('/<int:customer_id>', methods=['OPTIONS', 'PUT'])
def update_customer(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        data = request.json
        
        # Update fields
        if 'first_name' in data:
            customer.first_name = data['first_name']
        if 'last_name' in data:
            customer.last_name = data['last_name']
        if 'email' in data:
            # Check if email exists for other customer
            existing = Customer.query.filter(Customer.email == data['email'], Customer.id != customer_id).first()
            if existing:
                response = jsonify({'success': False, 'error': 'Email already exists'})
                return add_cors_headers(response), 400
            customer.email = data['email']
        if 'phone' in data:
            existing = Customer.query.filter(Customer.phone == data['phone'], Customer.id != customer_id).first()
            if existing:
                response = jsonify({'success': False, 'error': 'Phone number already exists'})
                return add_cors_headers(response), 400
            customer.phone = data['phone']
        if 'alternative_phone' in data:
            customer.alternative_phone = data['alternative_phone']
        if 'dob' in data:
            customer.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date() if data['dob'] else None
        if 'gender' in data:
            customer.gender = data['gender']
        if 'notes' in data:
            customer.notes = data['notes']
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer updated successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error updating customer:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# DELETE CUSTOMER (Soft Delete with Tracking)
# ============================================================
@customer_bp.route('/<int:customer_id>', methods=['OPTIONS', 'DELETE'])
def delete_customer(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        # Check if already deleted
        if not customer.is_active:
            response = jsonify({'success': False, 'error': 'Customer is already deleted'})
            return add_cors_headers(response), 400
        
        # Soft delete with tracking
        customer.is_active = False
        customer.deleted_at = get_sl_time()
        # You can pass employee_id from JWT token if available
        # customer.deleted_by = request.employee_id
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': 'Customer deactivated successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error deleting customer:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# ADD ADDRESS
# ============================================================
@customer_bp.route('/<int:customer_id>/addresses', methods=['OPTIONS', 'POST'])
def add_address(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        data = request.json
        
        # If this is default, unset other defaults
        if data.get('is_default', False):
            for addr in customer.addresses:
                addr.is_default = False
        
        address = CustomerAddress(
            customer_id=customer_id,
            type=data.get('type', 'home'),
            is_default=data.get('is_default', False),
            address_line1=data['address_line1'],
            address_line2=data.get('address_line2'),
            city=data['city'],
            postal_code=data.get('postal_code')
        )
        
        db.session.add(address)
        
        # If this is the first address, make it default
        if len(customer.addresses) == 0:
            address.is_default = True
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': address.to_dict(),
            'message': 'Address added successfully'
        })
        return add_cors_headers(response), 201
    except Exception as e:
        db.session.rollback()
        print('Error adding address:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# UPDATE ADDRESS
# ============================================================
@customer_bp.route('/<int:customer_id>/addresses/<int:address_id>', methods=['OPTIONS', 'PUT'])
def update_address(customer_id, address_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        address = CustomerAddress.query.filter_by(id=address_id, customer_id=customer_id).first()
        if not address:
            response = jsonify({'success': False, 'error': 'Address not found'})
            return add_cors_headers(response), 404
        
        data = request.json
        
        # If setting as default, unset others
        if data.get('is_default', False):
            customer = Customer.query.get(customer_id)
            for addr in customer.addresses:
                addr.is_default = (addr.id == address_id)
        
        address.type = data.get('type', address.type)
        address.is_default = data.get('is_default', address.is_default)
        address.address_line1 = data.get('address_line1', address.address_line1)
        address.address_line2 = data.get('address_line2', address.address_line2)
        address.city = data.get('city', address.city)
        address.postal_code = data.get('postal_code', address.postal_code)
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': address.to_dict(),
            'message': 'Address updated successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error updating address:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# DELETE ADDRESS
# ============================================================
@customer_bp.route('/<int:customer_id>/addresses/<int:address_id>', methods=['OPTIONS', 'DELETE'])
def delete_address(customer_id, address_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        address = CustomerAddress.query.filter_by(id=address_id, customer_id=customer_id).first()
        if not address:
            response = jsonify({'success': False, 'error': 'Address not found'})
            return add_cors_headers(response), 404
        
        # If deleting default, set another as default
        if address.is_default:
            customer = Customer.query.get(customer_id)
            other_addresses = [a for a in customer.addresses if a.id != address_id]
            if other_addresses:
                other_addresses[0].is_default = True
        
        db.session.delete(address)
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Address deleted successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error deleting address:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# SET DEFAULT ADDRESS
# ============================================================
@customer_bp.route('/<int:customer_id>/addresses/<int:address_id>/default', methods=['OPTIONS', 'PUT'])
def set_default_address(customer_id, address_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        for addr in customer.addresses:
            addr.is_default = (addr.id == address_id)
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Default address updated successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error setting default address:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# ADD NOTE
# ============================================================
@customer_bp.route('/<int:customer_id>/notes', methods=['OPTIONS', 'POST'])
def add_note(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        data = request.json
        customer.notes = data.get('note')
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Note added successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error adding note:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# ADD LOYALTY POINTS
# ============================================================
@customer_bp.route('/<int:customer_id>/points', methods=['OPTIONS', 'POST'])
def add_points(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            response = jsonify({'success': False, 'error': 'Customer not found'})
            return add_cors_headers(response), 404
        
        data = request.json
        points = data.get('points', 0)
        reason = data.get('reason', 'Manual adjustment')
        
        if points <= 0:
            response = jsonify({'success': False, 'error': 'Points must be greater than 0'})
            return add_cors_headers(response), 400
        
        old_points = customer.loyalty_points
        customer.loyalty_points += points
        customer.update_tier()
        
        # Log transaction
        transaction = LoyaltyTransaction(
            customer_id=customer_id,
            points=points,
            balance_after=customer.loyalty_points,
            reason=reason,
            source='manual_add'
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'data': {
                'customer': customer.to_dict(),
                'transaction': transaction.to_dict()
            },
            'message': f'Added {points} points successfully'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        print('Error adding points:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# GET POINTS HISTORY
# ============================================================
@customer_bp.route('/<int:customer_id>/points/history', methods=['OPTIONS', 'GET'])
def get_points_history(customer_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        transactions = LoyaltyTransaction.query.filter_by(customer_id=customer_id).order_by(LoyaltyTransaction.created_at.desc()).all()
        response = jsonify({
            'success': True,
            'data': [t.to_dict() for t in transactions]
        })
        return add_cors_headers(response), 200
    except Exception as e:
        print('Error fetching points history:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500


# ============================================================
# GET CUSTOMER STATS
# ============================================================
@customer_bp.route('/stats', methods=['OPTIONS', 'GET'])
def get_customer_stats():
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response), 200
    
    try:
        total = Customer.query.filter_by(is_active=True).count()
        
        from datetime import datetime, timedelta
        start_of_month = datetime.now(SL_TIMEZONE).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = Customer.query.filter(Customer.created_at >= start_of_month).count()
        
        repeat_buyers = Customer.query.filter(Customer.total_orders >= 2).count()
        
        # Tier distribution
        tiers = {}
        for tier in ['bronze', 'silver', 'gold', 'platinum']:
            tiers[tier] = Customer.query.filter_by(tier=tier, is_active=True).count()
        
        response = jsonify({
            'success': True,
            'data': {
                'total': total,
                'new_this_month': new_this_month,
                'repeat_buyers': repeat_buyers,
                'tiers': tiers
            }
        })
        return add_cors_headers(response), 200
    except Exception as e:
        print('Error fetching stats:', str(e))
        response = jsonify({'success': False, 'error': str(e)})
        return add_cors_headers(response), 500
