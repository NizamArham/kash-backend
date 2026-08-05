from marshmallow import Schema, fields

class ProductVariantSchema(Schema):
    id = fields.Int(dump_only=True)
    color = fields.Str(required=True)
    size = fields.Str(required=True)
    quantity = fields.Int(required=True)
    sku = fields.Str(required=True)
    barcode = fields.Str()

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    product_name = fields.Str(required=True)
    description = fields.Str()
    category = fields.Str(required=True)
    sub_category = fields.Str(required=True)
    gender = fields.Str()
    brand = fields.Str()
    base_price = fields.Decimal(required=True)
    cost_price = fields.Decimal()
    weight = fields.Decimal()
    keywords = fields.List(fields.Str())
    status = fields.Str()
    total_quantity = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    variants = fields.Nested(ProductVariantSchema, many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
