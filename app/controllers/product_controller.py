from app.models import Product, ProductVariant
from app.extensions import db
from sqlalchemy import or_

class ProductController:
    
    @staticmethod
    def get_all_products(filters=None):
        query = Product.query
        
        if filters:
            if filters.get('category') and filters['category'] != 'all':
                query = query.filter(Product.category == filters['category'])
            if filters.get('brand') and filters['brand'] != 'all':
                query = query.filter(Product.brand == filters['brand'])
            if filters.get('status') and filters['status'] != 'all':
                query = query.filter(Product.status == filters['status'])
            if filters.get('search'):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Product.product_name.like(search),
                        Product.brand.like(search),
                        Product.category.like(search)
                    )
                )
        
        return query.order_by(Product.created_at.desc()).all()
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)
    
    @staticmethod
    def create_product(data):
        try:
            product = Product(
                product_name=data['product_name'],
                description=data.get('description'),
                category=data['category'],
                sub_category=data['sub_category'],
                gender=data.get('gender'),
                brand=data.get('brand'),
                base_price=float(data['base_price']),
                cost_price=float(data['cost_price']) if data.get('cost_price') else None,
                weight=float(data['weight']) if data.get('weight') else None,
                keywords=data.get('keywords', [])
            )
            
            db.session.add(product)
            db.session.flush()
            
            total_quantity = 0
            for variant_data in data.get('variants', []):
                variant = ProductVariant(
                    product_id=product.id,
                    color=variant_data['color'],
                    size=variant_data['size'],
                    quantity=int(variant_data['quantity']),
                    sku=variant_data['sku'],
                    barcode=variant_data.get('barcode')
                )
                db.session.add(variant)
                total_quantity += int(variant_data['quantity'])
            
            product.total_quantity = total_quantity
            product.status = 'out_of_stock' if total_quantity == 0 else 'low_stock' if total_quantity < 10 else 'active'
            
            db.session.commit()
            return product
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return False
        db.session.delete(product)
        db.session.commit()
        return True
