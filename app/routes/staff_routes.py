from flask import Blueprint, request, jsonify
from app.models import Employee, SystemAccess, SystemAccessLog
from app.extensions import db
from datetime import datetime
import pytz

staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')

# Sri Lanka Timezone
SL_TIMEZONE = pytz.timezone('Asia/Colombo')

def get_sl_time():
    """Return current Sri Lanka time"""
    return datetime.now(SL_TIMEZONE)

# ============================================================
# GET ALL STAFF (Including Terminated)
# ============================================================
@staff_bp.route('/all', methods=['OPTIONS', 'GET'])
def get_all_staff_including_terminated():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        employees = db.session.query(
            Employee,
            SystemAccess.username,
            SystemAccess.role.label('system_role'),
            SystemAccess.is_active,
            SystemAccess.last_login_at
        ).outerjoin(
            SystemAccess, Employee.id == SystemAccess.employee_id
        ).order_by(Employee.first_name).all()
        
        result = []
        for emp, username, system_role, is_active, last_login_at in employees:
            result.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'phone': emp.phone,
                'alternative_phone': emp.alternative_phone,
                'dob': emp.dob.isoformat() if emp.dob else None,
                'gender': emp.gender,
                'address1': emp.address1,
                'address2': emp.address2,
                'city': emp.city,
                'postal_code': emp.postal_code,
                'nic': emp.nic,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
                'department': emp.department,
                'position': emp.position,
                'base_salary': float(emp.base_salary) if emp.base_salary else None,
                'reports_to': emp.reports_to,
                'bank_name': emp.bank_name,
                'bank_branch': emp.bank_branch,
                'account_number': emp.account_number,
                'account_holder_name': emp.account_holder_name,
                'employee_status': emp.employee_status,
                'status_reason': emp.status_reason,
                'role': system_role or 'cashier',
                'username': username,
                'is_active': is_active,
                'last_login_at': last_login_at.isoformat() if last_login_at else None,
                'created_at': emp.created_at.isoformat() if emp.created_at else None,
                'updated_at': emp.updated_at.isoformat() if emp.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
        
    except Exception as e:
        print('Error fetching all staff:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# GET ACTIVE STAFF ONLY
# ============================================================
@staff_bp.route('', methods=['OPTIONS', 'GET'])
def get_all_staff():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        employees = db.session.query(
            Employee,
            SystemAccess.username,
            SystemAccess.role.label('system_role'),
            SystemAccess.is_active,
            SystemAccess.last_login_at
        ).outerjoin(
            SystemAccess, Employee.id == SystemAccess.employee_id
        ).filter(
            Employee.employee_status == 'active'
        ).order_by(Employee.first_name).all()
        
        result = []
        for emp, username, system_role, is_active, last_login_at in employees:
            result.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'phone': emp.phone,
                'alternative_phone': emp.alternative_phone,
                'dob': emp.dob.isoformat() if emp.dob else None,
                'gender': emp.gender,
                'address1': emp.address1,
                'address2': emp.address2,
                'city': emp.city,
                'postal_code': emp.postal_code,
                'nic': emp.nic,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
                'department': emp.department,
                'position': emp.position,
                'base_salary': float(emp.base_salary) if emp.base_salary else None,
                'reports_to': emp.reports_to,
                'bank_name': emp.bank_name,
                'bank_branch': emp.bank_branch,
                'account_number': emp.account_number,
                'account_holder_name': emp.account_holder_name,
                'employee_status': emp.employee_status,
                'status_reason': emp.status_reason,
                'role': system_role or 'cashier',
                'username': username,
                'is_active': is_active,
                'last_login_at': last_login_at.isoformat() if last_login_at else None,
                'created_at': emp.created_at.isoformat() if emp.created_at else None,
                'updated_at': emp.updated_at.isoformat() if emp.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
        
    except Exception as e:
        print('Error fetching staff:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# CREATE STAFF
# ============================================================
@staff_bp.route('', methods=['OPTIONS', 'POST'])
def create_staff():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        
        existing = Employee.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        existing = Employee.query.filter_by(phone=data['phone']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
        
        existing = Employee.query.filter_by(nic=data['nic']).first()
        if existing:
            return jsonify({'success': False, 'error': 'NIC already exists'}), 400
        
        employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            alternative_phone=data.get('alternative_phone'),
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            gender=data['gender'],
            address1=data['address1'],
            address2=data.get('address2'),
            city=data['city'],
            postal_code=data.get('postal_code'),
            nic=data['nic'],
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
            department=data.get('department'),
            position=data['position'],
            base_salary=float(data['base_salary']),
            reports_to=int(data['reports_to']) if data.get('reports_to') else None,
            bank_name=data['bank_name'],
            bank_branch=data.get('bank_branch'),
            account_number=data['account_number'],
            account_holder_name=data['account_holder_name'],
            employee_status='active'
        )
        
        employee.generate_employee_id()
        db.session.add(employee)
        db.session.flush()
        
        if data.get('is_active', True) and data.get('username'):
            password_hash, salt = SystemAccess.hash_password(data['password'])
            system_access = SystemAccess(
                employee_id=employee.id,
                username=data['username'],
                password_hash=password_hash,
                salt=salt,
                role=data.get('role', 'cashier'),
                is_active=True
            )
            db.session.add(system_access)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': employee.to_dict(),
            'message': 'Staff member created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print('Error creating staff:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# GET SINGLE STAFF
# ============================================================
@staff_bp.route('/<int:employee_id>', methods=['OPTIONS', 'GET'])
def get_staff(employee_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        emp = db.session.query(
            Employee,
            SystemAccess.username,
            SystemAccess.role.label('system_role'),
            SystemAccess.is_active,
            SystemAccess.last_login_at
        ).outerjoin(
            SystemAccess, Employee.id == SystemAccess.employee_id
        ).filter(
            Employee.id == employee_id
        ).first()
        
        if not emp:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        employee, username, system_role, is_active, last_login_at = emp
        
        result = {
            'id': employee.id,
            'employee_id': employee.employee_id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': employee.phone,
            'alternative_phone': employee.alternative_phone,
            'dob': employee.dob.isoformat() if employee.dob else None,
            'gender': employee.gender,
            'address1': employee.address1,
            'address2': employee.address2,
            'city': employee.city,
            'postal_code': employee.postal_code,
            'nic': employee.nic,
            'hire_date': employee.hire_date.isoformat() if employee.hire_date else None,
            'department': employee.department,
            'position': employee.position,
            'base_salary': float(employee.base_salary) if employee.base_salary else None,
            'reports_to': employee.reports_to,
            'bank_name': employee.bank_name,
            'bank_branch': employee.bank_branch,
            'account_number': employee.account_number,
            'account_holder_name': employee.account_holder_name,
            'employee_status': employee.employee_status,
            'status_reason': employee.status_reason,
            'role': system_role or 'cashier',
            'username': username,
            'is_active': is_active,
            'last_login_at': last_login_at.isoformat() if last_login_at else None,
            'created_at': employee.created_at.isoformat() if employee.created_at else None,
            'updated_at': employee.updated_at.isoformat() if employee.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print('Error fetching staff:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# DELETE STAFF (Soft Delete)
# ============================================================
@staff_bp.route('/<int:employee_id>', methods=['OPTIONS', 'DELETE'])
def delete_staff(employee_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        return response, 200
    
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        employee.employee_status = 'terminated'
        employee.status_reason = 'Deleted by admin'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Staff member deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# STAFF LOGIN - ✅ WITH LOGGING & CORS
# ============================================================
@staff_bp.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        ip_address = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        session_id = request.headers.get('X-Session-ID', 'Unknown')
        
        system_access = SystemAccess.query.filter_by(username=username, is_active=True).first()
        if not system_access:
            # Log failed login - user not found
            employee = Employee.query.filter_by(username=username).first()
            if employee:
                log = SystemAccessLog(
                    employee_id=employee.id,
                    action='login_failed',
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status='failed',
                    failure_reason='Invalid username'
                )
            else:
                log = SystemAccessLog(
                    employee_id=None,
                    action='login_failed',
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status='failed',
                    failure_reason='User not found'
                )
            db.session.add(log)
            db.session.commit()
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        employee = Employee.query.get(system_access.employee_id)
        if employee.employee_status != 'active':
            log = SystemAccessLog(
                employee_id=employee.id,
                action='login_failed',
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                failure_reason='Account not active'
            )
            db.session.add(log)
            db.session.commit()
            return jsonify({'success': False, 'error': 'Account is not active'}), 403
        
        if not SystemAccess.verify_password(password, system_access.password_hash, system_access.salt):
            system_access.failed_attempts += 1
            system_access.last_failed_attempt = get_sl_time()
            
            log = SystemAccessLog(
                employee_id=employee.id,
                action='login_failed',
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                status='failed',
                failure_reason='Incorrect password'
            )
            db.session.add(log)
            db.session.commit()
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        system_access.failed_attempts = 0
        system_access.last_login_at = get_sl_time()
        system_access.current_session_id = session_id
        db.session.commit()
        
        # Log successful login
        log = SystemAccessLog(
            employee_id=employee.id,
            action='login',
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'employee': employee.to_dict(),
                'access': system_access.to_dict()
            },
            'message': 'Login successful'
        })
        
    except Exception as e:
        print('Login error:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# STAFF LOGOUT - ✅ WITH LOGGING & CORS
# ============================================================
@staff_bp.route('/logout', methods=['OPTIONS', 'POST'])
def logout():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        employee_id = data.get('employee_id')
        session_id = data.get('session_id', 'unknown')
        ip_address = request.remote_addr or 'Unknown'
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Update system_access - clear session
        system_access = SystemAccess.query.filter_by(employee_id=employee_id).first()
        if system_access:
            system_access.current_session_id = None
            system_access.last_logout_at = get_sl_time()
            db.session.commit()
        
        # Log the logout
        log = SystemAccessLog(
            employee_id=employee_id,
            action='logout',
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
        
    except Exception as e:
        print('Logout error:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# VERIFY PASSWORD
# ============================================================
@staff_bp.route('/verify-password', methods=['OPTIONS', 'POST'])
def verify_password():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        system_access = SystemAccess.query.filter_by(username=username).first()
        if not system_access:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if SystemAccess.verify_password(password, system_access.password_hash, system_access.salt):
            return jsonify({'success': True, 'message': 'Password verified'})
        else:
            return jsonify({'success': False, 'error': 'Incorrect password'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# GET ACCESS LOGS
# ============================================================
@staff_bp.route('/logs', methods=['OPTIONS', 'GET'])
def get_access_logs():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        logs = SystemAccessLog.query.order_by(SystemAccessLog.created_at.desc()).limit(100).all()
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs],
            'count': len(logs)
        })
    except Exception as e:
        print('Error fetching logs:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# FILTER OPTIONS
# ============================================================
@staff_bp.route('/filter-options', methods=['OPTIONS', 'GET'])
def get_filter_options():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        roles = db.session.query(SystemAccess.role.distinct()).filter(
            SystemAccess.role.isnot(None)
        ).all()
        role_list = ['all'] + [r[0] for r in roles if r[0]]
        
        departments = db.session.query(Employee.department.distinct()).filter(
            Employee.department.isnot(None),
            Employee.department != ''
        ).all()
        dept_list = ['all'] + [d[0] for d in departments if d[0]]
        
        status_list = ['all', 'active', 'on_leave', 'suspended', 'terminated', 'left']
        
        return jsonify({
            'success': True,
            'data': {
                'roles': role_list,
                'departments': dept_list,
                'statuses': status_list
            }
        })
        
    except Exception as e:
        print('Error fetching filter options:', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500
