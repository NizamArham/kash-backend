from flask import Blueprint, request, jsonify
from app.controllers.product_controller import ProductController
from app.schemas.product_schema import product_schema, products_schema

product_bp = Blueprint('product', __name__, url_prefix='/api/inventory')

# ============================================================
# GET ALL PRODUCTS
# ============================================================
@product_bp.route('', methods=['GET', 'OPTIONS'])
def get_products():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
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

# ============================================================
# CREATE PRODUCT
# ============================================================
@product_bp.route('', methods=['POST', 'OPTIONS'])
def create_product():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        product = ProductController.create_product(data)
        result = product_schema.dump(product)
        return jsonify({'success': True, 'data': result, 'message': 'Product created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# GET SINGLE PRODUCT
# ============================================================
@product_bp.route('/<int:product_id>', methods=['GET', 'OPTIONS'])
def get_product(product_id):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    try:
        product = ProductController.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        result = product_schema.dump(product)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# UPDATE PRODUCT
# ============================================================
@product_bp.route('/<int:product_id>', methods=['PUT', 'OPTIONS'])
def update_product(product_id):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        product = ProductController.update_product(product_id, data)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        result = product_schema.dump(product)
        return jsonify({'success': True, 'data': result, 'message': 'Product updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# DELETE PRODUCT
# ============================================================
@product_bp.route('/<int:product_id>', methods=['DELETE', 'OPTIONS'])
def delete_product(product_id):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        return response, 200
    
    try:
        success = ProductController.delete_product(product_id)
        if not success:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# UPDATE VARIANT STOCK (NEW ENDPOINT)
# ============================================================
@product_bp.route('/<int:product_id>/variants/<int:variant_id>', methods=['PUT', 'OPTIONS'])
def update_variant(product_id, variant_id):
    """Update a specific variant's stock/quantity"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        print(f"📦 Updating variant {variant_id} for product {product_id} with data: {data}")
        
        # Find the product
        product = ProductController.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Find the variant within the product
        variant = None
        variant_index = -1
        for idx, v in enumerate(product.variants):
            if v.id == variant_id:
                variant = v
                variant_index = idx
                break
        
        if not variant:
            return jsonify({'success': False, 'error': 'Variant not found'}), 404
        
        # Update variant fields
        updates = {}
        if 'quantity' in data:
            variant.quantity = int(data['quantity'])
            updates['quantity'] = variant.quantity
        if 'price' in data:
            variant.price = float(data['price'])
            updates['price'] = variant.price
        if 'sku' in data:
            variant.sku = data['sku']
            updates['sku'] = variant.sku
        if 'barcode' in data:
            variant.barcode = data['barcode']
            updates['barcode'] = variant.barcode
        if 'size' in data:
            variant.size = data['size']
            updates['size'] = variant.size
        if 'color' in data:
            variant.color = data['color']
            updates['color'] = variant.color
        
        # Save the updated product
        ProductController.update_product(product_id, {'variants': product.variants})
        
        return jsonify({
            'success': True,
            'data': {
                'variant': {
                    'id': variant.id,
                    'sku': variant.sku,
                    'barcode': variant.barcode,
                    'size': variant.size,
                    'color': variant.color,
                    'quantity': variant.quantity,
                    'price': variant.price
                }
            },
            'message': 'Variant updated successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating variant: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# BULK UPDATE VARIANTS (For updating stock in bulk)
# ============================================================
@product_bp.route('/variants/bulk', methods=['PUT', 'OPTIONS'])
def bulk_update_variants():
    """Update multiple variants at once"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        return response, 200
    
    try:
        data = request.json
        updates = data.get('variants', [])
        
        updated = []
        for update in updates:
            product_id = update.get('product_id')
            variant_id = update.get('variant_id')
            quantity = update.get('quantity')
            
            if not product_id or not variant_id or quantity is None:
                continue
            
            product = ProductController.get_product_by_id(product_id)
            if not product:
                continue
            
            variant = None
            for v in product.variants:
                if v.id == variant_id:
                    variant = v
                    break
            
            if variant:
                variant.quantity = int(quantity)
                ProductController.update_product(product_id, {'variants': product.variants})
                updated.append({
                    'variant_id': variant_id,
                    'product_id': product_id,
                    'quantity': variant.quantity
                })
        
        return jsonify({
            'success': True,
            'data': updated,
            'message': f'Updated {len(updated)} variants'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    