"""add_ip_whitelist

Revision ID: a12489ca71f0
Revises: bbee7c1d716d
Create Date: 2026-01-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a12489ca71f0'
down_revision = 'bbee7c1d716d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 ip_whitelists 表
    op.create_table(
        'ip_whitelists',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ip_address', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['provider_configs.id'], ondelete='CASCADE'),
    )
    
    # 创建索引
    op.create_index('ix_ip_whitelists_ip_address', 'ip_whitelists', ['ip_address'])
    op.create_index('ix_ip_whitelists_is_global', 'ip_whitelists', ['is_global'])
    op.create_index('ix_ip_whitelists_provider_id', 'ip_whitelists', ['provider_id'])
    op.create_index('ix_ip_whitelists_is_enabled', 'ip_whitelists', ['is_enabled'])


def downgrade() -> None:
    # 删除索引和表
    op.drop_index('ix_ip_whitelists_is_enabled', table_name='ip_whitelists')
    op.drop_index('ix_ip_whitelists_provider_id', table_name='ip_whitelists')
    op.drop_index('ix_ip_whitelists_is_global', table_name='ip_whitelists')
    op.drop_index('ix_ip_whitelists_ip_address', table_name='ip_whitelists')
    op.drop_table('ip_whitelists')
