# app/routes/__init__.py
from app.routes.product_routes import product_bp
from app.routes.staff_routes import staff_bp
from app.routes.customer_routes import customer_bp
from app.routes.pos_routes import pos_bp
from app.routes.ledger_routes import ledger_bp  

__all__ = ['product_bp', 'staff_bp', 'customer_bp', 'pos_bp', 'ledger_bp']