from app.extensions import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    alternative_phone = db.Column(db.String(20))
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=False)
    address1 = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    nic = db.Column(db.String(20), unique=True, nullable=False)
    
    # Employment Information
    hire_date = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100), nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False)
    reports_to = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'))
    
    # Bank Details
    bank_name = db.Column(db.String(100), nullable=False)
    bank_branch = db.Column(db.String(100))
    account_number = db.Column(db.String(50), nullable=False)
    account_holder_name = db.Column(db.String(255), nullable=False)
    
    # Status Management
    employee_status = db.Column(db.Enum('active', 'on_leave', 'suspended', 'terminated'), default='active')
    status_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reports_to_employee = db.relationship('Employee', remote_side=[id], backref='subordinates')
    system_access = db.relationship('SystemAccess', backref='employee', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'phone': self.phone,
            'alternative_phone': self.alternative_phone,
            'dob': self.dob.isoformat() if self.dob else None,
            'gender': self.gender,
            'address1': self.address1,
            'address2': self.address2,
            'city': self.city,
            'postal_code': self.postal_code,
            'nic': self.nic,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'department': self.department,
            'position': self.position,
            'base_salary': float(self.base_salary) if self.base_salary else None,
            'reports_to': self.reports_to,
            'bank_name': self.bank_name,
            'bank_branch': self.bank_branch,
            'account_number': self.account_number,
            'account_holder_name': self.account_holder_name,
            'employee_status': self.employee_status,
            'status_reason': self.status_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def generate_employee_id(self):
        if not self.employee_id:
            last = Employee.query.order_by(Employee.id.desc()).first()
            if last and last.employee_id:
                try:
                    num = int(last.employee_id.split('-')[1]) + 1
                except:
                    num = 1
            else:
                num = 1
            self.employee_id = f"EMP-{str(num).zfill(3)}"
        return self.employee_id
