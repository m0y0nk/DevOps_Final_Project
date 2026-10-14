"""initial migration: inventory_items, checkouts, activity_events

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('quantity_total', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('quantity_available', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('low_stock_threshold', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('condition', sa.String(length=50), nullable=False, server_default='good'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('quantity_total >= 0', name='check_positive_total'),
        sa.CheckConstraint('quantity_available >= 0', name='check_positive_available'),
        sa.CheckConstraint('quantity_available <= quantity_total', name='check_available_le_total'),
        sa.CheckConstraint('low_stock_threshold >= 0', name='check_positive_low_stock'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_id'), 'inventory_items', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_items_name'), 'inventory_items', ['name'], unique=False)
    op.create_index(op.f('ix_inventory_items_sku'), 'inventory_items', ['sku'], unique=True)
    op.create_index(op.f('ix_inventory_items_category'), 'inventory_items', ['category'], unique=False)

    # 2. checkouts table
    op.create_table(
        'checkouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('borrower_name', sa.String(length=255), nullable=False),
        sa.Column('borrower_contact', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('checked_out_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('returned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='checked_out'),
        sa.CheckConstraint('quantity > 0', name='check_positive_checkout_quantity'),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkouts_id'), 'checkouts', ['id'], unique=False)
    op.create_index(op.f('ix_checkouts_item_id'), 'checkouts', ['item_id'], unique=False)
    op.create_index(op.f('ix_checkouts_status'), 'checkouts', ['status'], unique=False)

    # 3. activity_events table
    op.create_table(
        'activity_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_events_id'), 'activity_events', ['id'], unique=False)
    op.create_index(op.f('ix_activity_events_event_type'), 'activity_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_activity_events_item_id'), 'activity_events', ['item_id'], unique=False)


def downgrade() -> None:
    op.drop_table('activity_events')
    op.drop_table('checkouts')
    op.drop_table('inventory_items')
