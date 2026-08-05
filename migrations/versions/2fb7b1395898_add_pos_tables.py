"""Add POS tables

Revision ID: 2fb7b1395898
Revises: c1728a158462
Create Date: 2026-07-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2fb7b1395898'
down_revision = 'c1728a158462'
branch_labels = None
depends_on = None

def upgrade():
    # Create delivery_partners table
    op.create_table('delivery_partners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('order_type', mysql.ENUM('in-store', 'online'), nullable=True),
        sa.Column('order_status', mysql.ENUM('pending', 'processing', 'completed', 'cancelled', 'shipped', 'delivered'), nullable=True),
        sa.Column('payment_method', mysql.ENUM('cash', 'card', 'bank_transfer', 'full_online', 'products_online', 'delivery_online', 'full_cod'), nullable=True),
        sa.Column('payment_status', mysql.ENUM('pending', 'paid', 'failed', 'refunded'), nullable=True),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_total', sa.Numeric(10, 2), nullable=True),
        sa.Column('delivery_fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('cash_received', sa.Numeric(10, 2), nullable=True),
        sa.Column('change_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('loyalty_points_used', sa.Integer(), nullable=True),
        sa.Column('loyalty_points_earned', sa.Integer(), nullable=True),
        sa.Column('coupon_code', sa.String(length=50), nullable=True),
        sa.Column('coupon_discount', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('delivery_partner_id', sa.Integer(), nullable=True),
        sa.Column('shipping_tracking_no', sa.String(length=100), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('cod_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('cod_collected', sa.Boolean(), nullable=True),
        sa.Column('cod_collected_date', sa.DateTime(), nullable=True),
        sa.Column('courier_payment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['staff_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['delivery_partner_id'], ['delivery_partners.id'], ondelete='SET NULL')
    )
    
    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_variant_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], )
    )
    
    # Create courier_cod_ledger table
    op.create_table('courier_cod_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('delivery_partner_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', mysql.ENUM('order_cod', 'payment_received', 'adjustment'), nullable=False),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('debit', sa.Numeric(10, 2), nullable=True),
        sa.Column('credit', sa.Numeric(10, 2), nullable=True),
        sa.Column('balance', sa.Numeric(10, 2), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['delivery_partner_id'], ['delivery_partners.id'], )
    )
    
    # Create cashier_ledger table
    op.create_table('cashier_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cashier_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', mysql.ENUM('sale', 'refund', 'payment_received', 'cash_withdrawal', 'cash_deposit', 'expense', 'adjustment'), nullable=False),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('debit', sa.Numeric(10, 2), nullable=True),
        sa.Column('credit', sa.Numeric(10, 2), nullable=True),
        sa.Column('balance', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_method', mysql.ENUM('cash', 'card', 'bank_transfer', 'online'), nullable=True),
        sa.Column('payment_details', sa.JSON(), nullable=True),
        sa.Column('transaction_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['cashier_id'], ['employees.id'], )
    )
    
    # Insert default delivery partners
    op.execute("""
        INSERT INTO delivery_partners (name, code, fee, is_active) VALUES 
        ('CityPack by Advantis', 'citypack', 400, 1),
        ('DEX by Daraz', 'dex', 400, 1),
        ('M&M Express (Local Delivery)', 'mnm', 200, 1),
        ('Store Pickup', 'pickup', 0, 1)
    """)
    
    # Create indexes
    op.create_index('idx_order_number', 'orders', ['order_number'])
    op.create_index('idx_customer', 'orders', ['customer_id'])
    op.create_index('idx_staff', 'orders', ['staff_id'])
    op.create_index('idx_status', 'orders', ['order_status'])
    op.create_index('idx_created', 'orders', ['created_at'])
    op.create_index('idx_payment_status', 'orders', ['payment_status'])
    op.create_index('idx_delivery_partner', 'orders', ['delivery_partner_id'])
    op.create_index('idx_cod_status', 'orders', ['cod_collected'])
    op.create_index('idx_order', 'order_items', ['order_id'])
    op.create_index('idx_variant', 'order_items', ['product_variant_id'])
    op.create_index('idx_sku', 'order_items', ['sku'])
    op.create_index('idx_partner', 'courier_cod_ledger', ['delivery_partner_id'])
    op.create_index('idx_transaction_date', 'courier_cod_ledger', ['transaction_date'])
    op.create_index('idx_reference', 'courier_cod_ledger', ['reference_id'])
    op.create_index('idx_cashier', 'cashier_ledger', ['cashier_id'])
    op.create_index('idx_transaction_date', 'cashier_ledger', ['transaction_date'])
    op.create_index('idx_reference', 'cashier_ledger', ['reference_id'])
    op.create_index('idx_type', 'cashier_ledger', ['transaction_type'])
    op.create_index('idx_payment_method', 'cashier_ledger', ['payment_method'])

def downgrade():
    # Drop tables in reverse order
    op.drop_index('idx_payment_method', table_name='cashier_ledger')
    op.drop_index('idx_type', table_name='cashier_ledger')
    op.drop_index('idx_reference', table_name='cashier_ledger')
    op.drop_index('idx_transaction_date', table_name='cashier_ledger')
    op.drop_index('idx_cashier', table_name='cashier_ledger')
    op.drop_table('cashier_ledger')
    
    op.drop_index('idx_reference', table_name='courier_cod_ledger')
    op.drop_index('idx_transaction_date', table_name='courier_cod_ledger')
    op.drop_index('idx_partner', table_name='courier_cod_ledger')
    op.drop_table('courier_cod_ledger')
    
    op.drop_index('idx_sku', table_name='order_items')
    op.drop_index('idx_variant', table_name='order_items')
    op.drop_index('idx_order', table_name='order_items')
    op.drop_table('order_items')
    
    op.drop_index('idx_cod_status', table_name='orders')
    op.drop_index('idx_delivery_partner', table_name='orders')
    op.drop_index('idx_payment_status', table_name='orders')
    op.drop_index('idx_created', table_name='orders')
    op.drop_index('idx_status', table_name='orders')
    op.drop_index('idx_staff', table_name='orders')
    op.drop_index('idx_customer', table_name='orders')
    op.drop_index('idx_order_number', table_name='orders')
    op.drop_table('orders')
    
    op.drop_table('delivery_partners')
