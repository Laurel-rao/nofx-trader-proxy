"""add_billing_fields

Revision ID: 02f2724493fa
Revises: 5c7974e45bb3
Create Date: 2026-01-13 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02f2724493fa'
down_revision = '5c7974e45bb3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加计费字段到 provider_configs 表
    op.add_column('provider_configs', sa.Column('model_rate', sa.Numeric(10, 4), nullable=True, server_default='1.0'))
    op.add_column('provider_configs', sa.Column('completion_rate', sa.Numeric(10, 4), nullable=True, server_default='1.0'))
    op.add_column('provider_configs', sa.Column('group_rate', sa.Numeric(10, 4), nullable=True, server_default='1.0'))
    op.add_column('provider_configs', sa.Column('recharge_rate', sa.Numeric(10, 4), nullable=True, server_default='1.0'))
    
    # 添加计费字段到 request_logs 表
    op.add_column('request_logs', sa.Column('user_discount_rate', sa.Numeric(10, 4), nullable=True))
    op.add_column('request_logs', sa.Column('actual_cost', sa.Numeric(20, 6), nullable=True))
    op.add_column('request_logs', sa.Column('model_rate', sa.Numeric(10, 4), nullable=True))
    op.add_column('request_logs', sa.Column('completion_rate', sa.Numeric(10, 4), nullable=True))
    op.add_column('request_logs', sa.Column('group_rate', sa.Numeric(10, 4), nullable=True))
    op.add_column('request_logs', sa.Column('recharge_rate', sa.Numeric(10, 4), nullable=True))


def downgrade() -> None:
    # 删除 request_logs 表的计费字段
    op.drop_column('request_logs', 'recharge_rate')
    op.drop_column('request_logs', 'group_rate')
    op.drop_column('request_logs', 'completion_rate')
    op.drop_column('request_logs', 'model_rate')
    op.drop_column('request_logs', 'actual_cost')
    op.drop_column('request_logs', 'user_discount_rate')
    
    # 删除 provider_configs 表的计费字段
    op.drop_column('provider_configs', 'recharge_rate')
    op.drop_column('provider_configs', 'group_rate')
    op.drop_column('provider_configs', 'completion_rate')
    op.drop_column('provider_configs', 'model_rate')
