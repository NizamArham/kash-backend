from flask import Blueprint, request, jsonify
from app.controllers.product_controller import ProductController
from app.schemas.product_schema import product_schema, products_schema

product_bp = Blueprint('product', __name__, url_prefix='/api/inventory')

# Remove trailing slash requirement
@product_bp.route('', methods=['GET'])  # Changed from '/' to ''
def get_products():
    try:
        filters = {
            'category': request.args.get('category'),
            'brand': request.args.get('brand'),
            'status': request.args.get('status'),
            'search': request.args.get('search')
        }
        products = ProductController.get_all_products(filters)
        result = products_schema.dump(products)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('', methods=['POST'])  # Changed from '/' to ''
def create_product():
    try:
        data = request.json
        product = ProductController.create_product(data)
        result = product_schema.dump(product)
        return jsonify({'success': True, 'data': result, 'message': 'Product created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = ProductController.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        result = product_schema.dump(product)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        success = ProductController.delete_product(product_id)
        if not success:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
