# app/routes/ledger_routes.py
from flask import Blueprint, request, jsonify
from app.models.cashier_ledger import CashierLedger
from app.extensions import db
from datetime import datetime

ledger_bp = Blueprint('ledger', __name__, url_prefix='/api')

# ============================================================
# MAIN LEDGER ROUTES
# ============================================================

@ledger_bp.route('/ledger', methods=['GET'])
def get_ledger():
    """Get ledger entries with filters"""
    try:
        # Get query parameters
        cashier_id = request.args.get('cashier_id', type=int)
        transaction_type = request.args.get('type')
        payment_method = request.args.get('payment_method')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        only_posted = request.args.get('only_posted', 'true').lower() == 'true'
        include_unposted = request.args.get('include_unposted', 'false').lower() == 'true'
        
        # Get entries
        result = CashierLedger.get_ledger_entries(
            cashier_id=cashier_id,
            transaction_type=transaction_type,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            search_term=search,
            limit=limit,
            offset=offset,
            only_posted=only_posted,
            include_unposted=include_unposted
        )
        
        # Convert entries to dict with error handling
        entries_data = []
        for entry in result['entries']:
            try:
                entries_data.append(entry.to_dict())
            except Exception as e:
                print(f"Error converting entry {entry.id}: {str(e)}")
                entries_data.append({
                    'id': entry.id,
                    'cashier_id': entry.cashier_id,
                    'cashier_name': f"Employee #{entry.cashier_id}",
                    'transaction_type': entry.transaction_type,
                    'reference_id': entry.reference_id,
                    'description': entry.description,
                    'debit': float(entry.debit) if entry.debit else 0.00,
                    'credit': float(entry.credit) if entry.credit else 0.00,
                    'balance': float(entry.balance) if entry.balance else 0.00,
                    'payment_method': entry.payment_method,
                    'payment_details': entry.payment_details,
                    'session_id': entry.session_id,
                    'is_posted': entry.is_posted,
                    'posted_at': entry.posted_at.isoformat() if entry.posted_at else None,
                    'transaction_date': entry.transaction_date.isoformat() if entry.transaction_date else None,
                    'created_at': entry.created_at.isoformat() if entry.created_at else None,
                    'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
                })
        
        return jsonify({
            'success': True,
            'data': entries_data,
            'total': result['total'],
            'limit': result['limit'],
            'offset': result['offset']
        })
        
    except Exception as e:
        print(f"Error fetching ledger: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ledger_bp.route('/ledger/summary', methods=['GET'])
def get_ledger_summary():
    """Get ledger summary"""
    try:
        cashier_id = request.args.get('cashier_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        posted_only = request.args.get('posted_only', 'true').lower() == 'true'
        
        summary = CashierLedger.get_summary(
            cashier_id=cashier_id,
            start_date=start_date,
            end_date=end_date,
            posted_only=posted_only
        )
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        print(f"Error fetching ledger summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ledger_bp.route('/ledger/statement', methods=['GET'])
def get_ledger_statement():
    """Get full statement with opening/closing balance"""
    try:
        cashier_id = request.args.get('cashier_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        statement = CashierLedger.get_statement(
            cashier_id=cashier_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert entries to dict with error handling
        entries_data = []
        for entry in statement['entries']:
            try:
                entries_data.append(entry.to_dict())
            except Exception as e:
                print(f"Error converting entry {entry.id}: {str(e)}")
                entries_data.append({
                    'id': entry.id,
                    'cashier_id': entry.cashier_id,
                    'cashier_name': f"Employee #{entry.cashier_id}",
                    'transaction_type': entry.transaction_type,
                    'reference_id': entry.reference_id,
                    'description': entry.description,
                    'debit': float(entry.debit) if entry.debit else 0.00,
                    'credit': float(entry.credit) if entry.credit else 0.00,
                    'balance': float(entry.balance) if entry.balance else 0.00,
                    'payment_method': entry.payment_method,
                    'payment_details': entry.payment_details,
                    'session_id': entry.session_id,
                    'is_posted': entry.is_posted,
                    'posted_at': entry.posted_at.isoformat() if entry.posted_at else None,
                    'transaction_date': entry.transaction_date.isoformat() if entry.transaction_date else None,
                    'created_at': entry.created_at.isoformat() if entry.created_at else None,
                    'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
                })
        
        statement['entries'] = entries_data
        
        return jsonify({
            'success': True,
            'data': statement
        })
        
    except Exception as e:
        print(f"Error fetching ledger statement: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# SESSION MANAGEMENT ROUTES
# ============================================================

@ledger_bp.route('/ledger/session/start', methods=['POST'])
def start_session():
    """Start a new cashier session"""
    try:
        data = request.get_json()
        cashier_id = data.get('cashier_id')
        
        if not cashier_id:
            return jsonify({'success': False, 'error': 'cashier_id required'}), 400
        
        # Generate session ID for today
        session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Check if there's already an unposted session
        existing = CashierLedger.query.filter_by(
            cashier_id=cashier_id,
            session_id=session_id,
            is_posted=False
        ).first()
        
        if existing:
            return jsonify({
                'success': True,
                'message': 'Session already exists',
                'data': {
                    'session_id': session_id,
                    'cashier_id': cashier_id,
                    'started_at': datetime.utcnow().isoformat(),
                    'is_new': False
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'cashier_id': cashier_id,
                'started_at': datetime.utcnow().isoformat(),
                'is_new': True
            }
        })
        
    except Exception as e:
        print(f"Error starting session: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ledger_bp.route('/ledger/session/<int:cashier_id>', methods=['GET'])
def get_session_entries(cashier_id):
    """Get all unposted entries for a cashier's session"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        entries = CashierLedger.get_cashier_session(cashier_id, session_id)
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries],
            'total': len(entries),
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error fetching session entries: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ledger_bp.route('/ledger/session/summary', methods=['GET'])
def get_session_summary():
    """Get summary of unposted entries for a session"""
    try:
        cashier_id = request.args.get('cashier_id', type=int)
        session_id = request.args.get('session_id')
        
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        summary = CashierLedger.get_session_summary(cashier_id, session_id)
        
        # Convert entries to dict for JSON response
        entries_data = [entry.to_dict() for entry in summary['entries']]
        summary['entries'] = entries_data
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        print(f"Error fetching session summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ledger_bp.route('/ledger/session/post', methods=['POST'])
def post_session():
    """Post all unposted entries to main ledger"""
    try:
        data = request.get_json()
        cashier_id = data.get('cashier_id')
        session_id = data.get('session_id')
        
        if not cashier_id:
            return jsonify({'success': False, 'error': 'cashier_id required'}), 400
        
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        result = CashierLedger.post_session(cashier_id, session_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"Error posting session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@ledger_bp.route('/ledger/session/cancel', methods=['POST'])
def cancel_session():
    """Cancel/delete all unposted entries for a session"""
    try:
        data = request.get_json()
        cashier_id = data.get('cashier_id')
        session_id = data.get('session_id')
        
        if not cashier_id:
            return jsonify({'success': False, 'error': 'cashier_id required'}), 400
        
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Get all unposted entries
        entries = CashierLedger.query.filter_by(
            cashier_id=cashier_id,
            session_id=session_id,
            is_posted=False
        ).all()
        
        count = len(entries)
        
        # Delete them
        for entry in entries:
            db.session.delete(entry)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'message': f'Cancelled {count} entries',
                'count': count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelling session: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ledger_bp.route('/ledger/session/add', methods=['POST'])
def add_session_transaction():
    """Add a transaction to the current session"""
    try:
        data = request.get_json()
        cashier_id = data.get('cashier_id')
        session_id = data.get('session_id')
        transaction_type = data.get('type')
        amount = data.get('amount')
        description = data.get('description')
        payment_method = data.get('payment_method', 'cash')
        payment_details = data.get('payment_details')
        reference_id = data.get('reference_id')
        customer_name = data.get('customer_name')
        notes = data.get('notes')
        
        if not cashier_id:
            return jsonify({'success': False, 'error': 'cashier_id required'}), 400
        
        if not amount or amount <= 0:
            return jsonify({'success': False, 'error': 'Valid amount required'}), 400
        
        if not description:
            return jsonify({'success': False, 'error': 'Description required'}), 400
        
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Determine if this is cash in or cash out
        income_types = ['sale', 'payment_received', 'cash_deposit']
        
        if transaction_type in income_types:
            # Cash In
            entry = CashierLedger.cash_in(
                cashier_id=cashier_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                reference_id=reference_id,
                customer_name=customer_name,
                payment_method=payment_method,
                payment_details=payment_details,
                notes=notes,
                session_id=session_id
            )
        else:
            # Cash Out
            entry = CashierLedger.cash_out(
                cashier_id=cashier_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                reference_id=reference_id,
                payment_method=payment_method,
                payment_details=payment_details,
                notes=notes,
                session_id=session_id
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction added successfully',
            'data': entry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding transaction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500