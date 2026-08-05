# app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.config import config
from app.extensions import db, migrate
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure CORS
    CORS(app, 
         origins='*', 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'X-Session-ID'],
         expose_headers=['X-Session-ID']
    )
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes.product_routes import product_bp
    from app.routes.staff_routes import staff_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.pos_routes import pos_bp
    from app.routes.ledger_routes import ledger_bp  # ← Import ledger
    
    app.register_blueprint(product_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(ledger_bp)  # ← Register ledger blueprint
    
    @app.route('/api/test', methods=['GET'])
    def test():
        return {'success': True, 'message': 'Server is running!', 'status': 'ok'}
    
    return app