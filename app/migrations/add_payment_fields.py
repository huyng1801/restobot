"""Add payment fields to orders table

Revision ID: add_payment_fields
Revises: initial
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_payment_fields'
down_revision = 'initial'
branch_labels = None
depends_on = None


def upgrade():
    # Add payment_method column
    op.add_column('orders', sa.Column('payment_method', sa.String(), nullable=True))
    # Add payment_date column  
    op.add_column('orders', sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Remove payment columns
    op.drop_column('orders', 'payment_date')
    op.drop_column('orders', 'payment_method')