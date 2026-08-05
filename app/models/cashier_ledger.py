# app/models/cashier_ledger.py
from app.extensions import db
from datetime import datetime

class CashierLedger(db.Model):
    __tablename__ = 'cashier_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    cashier_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    
    transaction_type = db.Column(
        db.Enum('sale', 'refund', 'payment_received', 'cash_withdrawal', 
                'cash_deposit', 'expense', 'adjustment'), 
        nullable=False
    )
    
    reference_id = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.String(255), nullable=True)
    
    debit = db.Column(db.Numeric(10, 2), default=0.00)
    credit = db.Column(db.Numeric(10, 2), default=0.00)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    payment_method = db.Column(
        db.Enum('cash', 'card', 'bank_transfer', 'online', 'cod', 'mobile_payment'), 
        default='cash'
    )
    payment_details = db.Column(db.JSON, nullable=True)
    
    # NEW: Session and Posting tracking
    session_id = db.Column(db.String(100), nullable=True, index=True)
    is_posted = db.Column(db.Boolean, default=False, index=True)
    posted_at = db.Column(db.DateTime, nullable=True)
    
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cashier = db.relationship('Employee', backref='cashier_ledger_entries', foreign_keys=[cashier_id])
    
    
    # ============================================================
    # DESCRIPTION GENERATORS
    # ============================================================
    
    @staticmethod
    def generate_description(transaction_type, amount, reference_id=None, customer_name=None, 
                            payment_method=None, notes=None):
        """Generate a clear description based on transaction type"""
        
        amount_str = f"Rs. {amount:,.2f}"
        
        # For CASH OUT (no customer, no order)
        if transaction_type in ['cash_withdrawal', 'expense', 'adjustment']:
            type_label = transaction_type.replace('_', ' ').title()
            if notes:
                description = f"{type_label} - {notes}"
            else:
                description = f"{type_label}"
            
            # Add amount and payment method
            description += f" - Amount: {amount_str}"
            if payment_method:
                description += f" ({payment_method})"
            return description
        
        # For CASH IN (sales, refunds, payments)
        descriptions = {
            'sale': {
                'template': 'Sale - {reference} {customer} - Amount: {amount}',
                'fallback': 'Sale - {reference} - Amount: {amount}'
            },
            'refund': {
                'template': 'Refund - {reference} {customer} - Amount: {amount}',
                'fallback': 'Refund - {reference} - Amount: {amount}'
            },
            'payment_received': {
                'template': 'Payment Received - {reference} {customer} - Amount: {amount}',
                'fallback': 'Payment Received - {reference} - Amount: {amount}'
            },
            'cash_deposit': {
                'template': 'Cash Deposit - {notes} - Amount: {amount}',
                'fallback': 'Cash Deposit - Amount: {amount}'
            }
        }
        
        type_config = descriptions.get(transaction_type, descriptions.get('sale'))
        
        data = {
            'amount': amount_str,
            'reference': reference_id or 'N/A',
            'customer': f"- {customer_name}" if customer_name else '',
            'notes': notes or 'No details provided',
            'payment': payment_method or 'N/A'
        }
        
        if customer_name and reference_id:
            description = type_config['template'].format(**data)
        else:
            description = type_config['fallback'].format(**data)
        
        # Add payment method if not already included
        if payment_method and 'payment' not in description.lower():
            description += f" ({payment_method})"
        
        return description
    
    # ============================================================
    # SESSION MANAGEMENT
    # ============================================================
    
    @classmethod
    def get_or_create_session(cls, cashier_id, session_id=None):
        """Get or create a session for a cashier"""
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Check if there's an existing unposted session
        existing = cls.query.filter_by(
            cashier_id=cashier_id,
            session_id=session_id,
            is_posted=False
        ).first()
        
        if existing:
            return session_id
        
        return session_id
    
    @classmethod
    def get_cashier_session(cls, cashier_id, session_id=None):
        """Get all entries for a cashier's current session"""
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        return cls.query.filter_by(
            cashier_id=cashier_id,
            session_id=session_id,
            is_posted=False
        ).order_by(cls.transaction_date.asc()).all()
    
    @classmethod
    def post_session(cls, cashier_id, session_id=None):
        """Post all unposted entries for a cashier's session to main ledger"""
        entries = cls.get_cashier_session(cashier_id, session_id)
        
        if not entries:
            return {
                'success': False,
                'message': 'No entries to post',
                'count': 0
            }
        
        # Update all entries
        for entry in entries:
            entry.is_posted = True
            entry.posted_at = datetime.utcnow()
        
        db.session.commit()
        
        # Calculate totals
        total_debit = sum(float(e.debit) for e in entries)
        total_credit = sum(float(e.credit) for e in entries)
        
        return {
            'success': True,
            'message': f'Posted {len(entries)} entries',
            'count': len(entries),
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balance': total_credit - total_debit
        }
    
    @classmethod
    def get_session_summary(cls, cashier_id=None, session_id=None):
        """Get summary of unposted entries for a session"""
        query = cls.query.filter_by(is_posted=False)
        
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        entries = query.order_by(cls.transaction_date.asc()).all()
        
        total_debit = sum(float(e.debit) for e in entries)
        total_credit = sum(float(e.credit) for e in entries)
        
        # Count by type
        type_counts = {}
        for entry in entries:
            type_counts[entry.transaction_type] = type_counts.get(entry.transaction_type, 0) + 1
        
        return {
            'cashier_id': cashier_id,
            'session_id': session_id,
            'total_entries': len(entries),
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balance': total_credit - total_debit,
            'type_counts': type_counts,
            'entries': entries
        }
    
    # ============================================================
    # CASH IN METHODS (Money Coming IN) - With Session Tracking
    # ============================================================
    
    @classmethod
    def cash_in(cls, cashier_id, amount, transaction_type, description=None,
                reference_id=None, customer_name=None, payment_method='cash', 
                payment_details=None, notes=None, session_id=None):
        """
        Generic Cash In method - Money coming IN
        Used for: sales, payment_received, cash_deposit
        """
        if not description:
            description = cls.generate_description(
                transaction_type=transaction_type,
                amount=amount,
                reference_id=reference_id,
                customer_name=customer_name,
                payment_method=payment_method,
                notes=notes
            )
        
        # Get current session ID
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Get current balance (from posted entries only)
        current_balance = cls.get_running_balance(cashier_id)
        
        # Cash In = Credit (money IN)
        entry = cls(
            cashier_id=cashier_id,
            transaction_type=transaction_type,
            reference_id=reference_id,
            description=description,
            debit=0.00,
            credit=float(amount),
            balance=current_balance + float(amount),
            payment_method=payment_method,
            payment_details=payment_details or {"notes": notes or "Cash In"},
            session_id=session_id,
            is_posted=False,
            transaction_date=datetime.utcnow()
        )
        
        db.session.add(entry)
        return entry
    
    @classmethod
    def create_sale_entry(cls, cashier_id, amount, order_number, customer_name=None, 
                          payment_method='cash', payment_details=None, notes=None,
                          session_id=None):
        """Create a sale entry (CASH IN)"""
        return cls.cash_in(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='sale',
            reference_id=order_number,
            customer_name=customer_name,
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or f"Order #{order_number}",
            session_id=session_id
        )
    
    @classmethod
    def create_payment_received_entry(cls, cashier_id, amount, reference_id=None,
                                      customer_name=None, payment_method='cash',
                                      payment_details=None, notes=None, session_id=None):
        """Create a payment received entry (CASH IN)"""
        return cls.cash_in(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='payment_received',
            reference_id=reference_id,
            customer_name=customer_name,
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or "Payment Received",
            session_id=session_id
        )
    
    @classmethod
    def create_cash_deposit_entry(cls, cashier_id, amount, notes=None,
                                  payment_method='cash', payment_details=None, session_id=None):
        """Create a cash deposit entry (CASH IN)"""
        return cls.cash_in(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='cash_deposit',
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or "Cash Deposit",
            session_id=session_id
        )
    
    # ============================================================
    # CASH OUT METHODS (Money Going OUT) - With Session Tracking
    # ============================================================
    
    @classmethod
    def cash_out(cls, cashier_id, amount, transaction_type, description=None,
                 reference_id=None, payment_method='cash', payment_details=None, 
                 notes=None, session_id=None):
        """
        Generic Cash Out method - Money going OUT
        Used for: refund, cash_withdrawal, expense, adjustment
        """
        if not description:
            description = cls.generate_description(
                transaction_type=transaction_type,
                amount=amount,
                payment_method=payment_method,
                notes=notes
            )
        
        # Get current session ID
        if not session_id:
            session_id = datetime.utcnow().strftime('%Y%m%d')
        
        # Get current balance (from posted entries only)
        current_balance = cls.get_running_balance(cashier_id)
        
        # Cash Out = Debit (money OUT)
        entry = cls(
            cashier_id=cashier_id,
            transaction_type=transaction_type,
            reference_id=reference_id,
            description=description,
            debit=float(amount),
            credit=0.00,
            balance=current_balance - float(amount),
            payment_method=payment_method,
            payment_details=payment_details or {"notes": notes or "Cash Out"},
            session_id=session_id,
            is_posted=False,
            transaction_date=datetime.utcnow()
        )
        
        db.session.add(entry)
        return entry
    
    @classmethod
    def create_refund_entry(cls, cashier_id, amount, order_number, customer_name=None,
                           payment_method='cash', payment_details=None, notes=None,
                           session_id=None):
        """Create a refund entry (CASH OUT)"""
        return cls.cash_out(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='refund',
            reference_id=order_number,
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or f"Refund for Order #{order_number}",
            session_id=session_id
        )
    
    @classmethod
    def create_expense_entry(cls, cashier_id, amount, category=None, notes=None,
                            payment_method='cash', payment_details=None, session_id=None):
        """Create an expense entry (CASH OUT)"""
        return cls.cash_out(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='expense',
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or category or "Expense",
            session_id=session_id
        )
    
    @classmethod
    def create_cash_withdrawal_entry(cls, cashier_id, amount, notes=None,
                                    payment_method='cash', payment_details=None,
                                    session_id=None):
        """Create a cash withdrawal entry (CASH OUT)"""
        return cls.cash_out(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='cash_withdrawal',
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or "Cash Withdrawal",
            session_id=session_id
        )
    
    @classmethod
    def create_adjustment_entry(cls, cashier_id, amount, notes=None,
                               payment_method='cash', payment_details=None,
                               session_id=None):
        """Create an adjustment entry (CASH OUT)"""
        return cls.cash_out(
            cashier_id=cashier_id,
            amount=amount,
            transaction_type='adjustment',
            payment_method=payment_method,
            payment_details=payment_details,
            notes=notes or "Adjustment",
            session_id=session_id
        )
    
    # ============================================================
    # QUERY METHODS - Updated to filter by posted status
    # ============================================================
    
    @classmethod
    def get_running_balance(cls, cashier_id=None, include_unposted=False):
        """Get the latest balance for a cashier or global"""
        query = cls.query
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        if not include_unposted:
            query = query.filter_by(is_posted=True)
        last_entry = query.order_by(cls.transaction_date.desc()).first()
        return float(last_entry.balance) if last_entry else 0.00
    
    @classmethod
    def get_ledger_entries(cls, cashier_id=None, limit=1000, offset=0, 
                          transaction_type=None, payment_method=None, 
                          start_date=None, end_date=None, search_term=None,
                          include_unposted=False, only_posted=True):
        """Get ledger entries with filters"""
        query = cls.query
        
        # Apply filters
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        if payment_method:
            query = query.filter_by(payment_method=payment_method)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        # Filter by posted status
        if only_posted:
            query = query.filter_by(is_posted=True)
        elif not include_unposted:
            query = query.filter_by(is_posted=True)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    cls.description.ilike(search),
                    cls.reference_id.ilike(search)
                )
            )
        
        # Order by date descending
        query = query.order_by(cls.transaction_date.desc())
        total = query.count()
        entries = query.limit(limit).offset(offset).all()
        
        return {
            'total': total,
            'entries': entries,
            'limit': limit,
            'offset': offset
        }
    
    @classmethod
    def get_summary(cls, cashier_id=None, start_date=None, end_date=None, posted_only=True):
        """Get summary statistics for the ledger"""
        query = cls.query
        
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        if posted_only:
            query = query.filter_by(is_posted=True)
        
        # Calculate totals
        total_debit = db.session.query(db.func.sum(cls.debit)).filter(cls.id.in_(query.with_entities(cls.id))).scalar() or 0
        total_credit = db.session.query(db.func.sum(cls.credit)).filter(cls.id.in_(query.with_entities(cls.id))).scalar() or 0
        
        # Count by type
        type_counts = db.session.query(cls.transaction_type, db.func.count(cls.id)).filter(cls.id.in_(query.with_entities(cls.id))).group_by(cls.transaction_type).all()
        
        return {
            'total_debit': float(total_debit),
            'total_credit': float(total_credit),
            'balance': float(total_credit) - float(total_debit),
            'type_counts': {t: c for t, c in type_counts},
            'total_entries': query.count()
        }
    
    @classmethod
    def get_statement(cls, cashier_id=None, start_date=None, end_date=None):
        """Get a complete statement with opening and closing balances"""
        query = cls.query.filter_by(is_posted=True)
        
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        # Get all entries for the period
        entries = query.order_by(cls.transaction_date.asc()).all()
        
        # Calculate opening balance (balance before first transaction)
        opening_balance = 0.00
        if entries:
            first_entry = entries[0]
            opening_balance = float(first_entry.balance) - float(first_entry.credit or 0) + float(first_entry.debit or 0)
        
        # Calculate totals
        total_debit = sum(float(e.debit or 0) for e in entries)
        total_credit = sum(float(e.credit or 0) for e in entries)
        closing_balance = opening_balance + total_credit - total_debit
        
        return {
            'opening_balance': opening_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'closing_balance': closing_balance,
            'entries': entries,
            'total_entries': len(entries)
        }
    
    @classmethod
    def get_unposted_entries(cls, cashier_id=None, session_id=None):
        """Get all unposted entries for posting"""
        query = cls.query.filter_by(is_posted=False)
        
        if cashier_id:
            query = query.filter_by(cashier_id=cashier_id)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        return query.order_by(cls.transaction_date.asc()).all()
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        # Safely get cashier name
        cashier_name = 'Unknown'
        if self.cashier:
            if hasattr(self.cashier, 'full_name'):
                cashier_name = self.cashier.full_name
            elif hasattr(self.cashier, 'first_name') and hasattr(self.cashier, 'last_name'):
                cashier_name = f"{self.cashier.first_name} {self.cashier.last_name}".strip()
            elif hasattr(self.cashier, 'name'):
                cashier_name = self.cashier.name
        
        return {
            'id': self.id,
            'cashier_id': self.cashier_id,
            'cashier_name': cashier_name,
            'transaction_type': self.transaction_type,
            'transaction_type_label': self.get_transaction_type_label(),
            'reference_id': self.reference_id,
            'description': self.description,
            'debit': float(self.debit) if self.debit else 0.00,
            'credit': float(self.credit) if self.credit else 0.00,
            'balance': float(self.balance) if self.balance else 0.00,
            'payment_method': self.payment_method,
            'payment_method_label': self.get_payment_method_label(),
            'payment_details': self.payment_details,
            'session_id': self.session_id,
            'is_posted': self.is_posted,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_transaction_type_label(self):
        """Get human-readable transaction type label"""
        labels = {
            'sale': 'Sale',
            'refund': 'Refund',
            'payment_received': 'Payment Received',
            'cash_withdrawal': 'Cash Withdrawal',
            'cash_deposit': 'Cash Deposit',
            'expense': 'Expense',
            'adjustment': 'Adjustment'
        }
        return labels.get(self.transaction_type, self.transaction_type)
    
    def get_payment_method_label(self):
        """Get human-readable payment method label"""
        labels = {
            'cash': 'Cash',
            'card': 'Card',
            'bank_transfer': 'Bank Transfer',
            'online': 'Online Payment',
            'cod': 'Cash on Delivery',
            'mobile_payment': 'Mobile Payment'
        }
        return labels.get(self.payment_method, self.payment_method)
    
    def is_cash_in(self):
        """Check if this is a Cash In transaction"""
        return self.transaction_type in ['sale', 'payment_received', 'cash_deposit']
    
    def is_cash_out(self):
        """Check if this is a Cash Out transaction"""
        return self.transaction_type in ['refund', 'cash_withdrawal', 'expense', 'adjustment']
    
    def __repr__(self):
        return f'<CashierLedger {self.id} - {self.transaction_type} - {self.description}>'


# ============================================================
# CONSTANTS
# ============================================================

TRANSACTION_TYPES = {
    'sale': {'label': 'Sale', 'type': 'income', 'icon': '📈'},
    'refund': {'label': 'Refund', 'type': 'expense', 'icon': '↩️'},
    'payment_received': {'label': 'Payment Received', 'type': 'income', 'icon': '💳'},
    'cash_withdrawal': {'label': 'Cash Withdrawal', 'type': 'expense', 'icon': '💸'},
    'cash_deposit': {'label': 'Cash Deposit', 'type': 'income', 'icon': '🏦'},
    'expense': {'label': 'Expense', 'type': 'expense', 'icon': '📉'},
    'adjustment': {'label': 'Adjustment', 'type': 'adjustment', 'icon': '⚖️'}
}

PAYMENT_METHODS = {
    'cash': {'label': 'Cash', 'icon': '💵'},
    'card': {'label': 'Card', 'icon': '💳'},
    'bank_transfer': {'label': 'Bank Transfer', 'icon': '🏦'},
    'online': {'label': 'Online Payment', 'icon': '🌐'},
    'cod': {'label': 'Cash on Delivery', 'icon': '📦'},
    'mobile_payment': {'label': 'Mobile Payment', 'icon': '📱'}
}

CASH_IN_TYPES = ['sale', 'payment_received', 'cash_deposit']
CASH_OUT_TYPES = ['refund', 'cash_withdrawal', 'expense', 'adjustment']