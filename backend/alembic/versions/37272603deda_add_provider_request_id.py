"""add_provider_request_id

Revision ID: 37272603deda
Revises: 02f2724493fa
Create Date: 2026-01-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '37272603deda'
down_revision = '02f2724493fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加供应商请求ID字段到 request_logs 表
    op.add_column('request_logs', sa.Column('provider_request_id', sa.String(255), nullable=True))
    op.create_index('ix_request_logs_provider_request_id', 'request_logs', ['provider_request_id'])


def downgrade() -> None:
    # 删除索引和字段
    op.drop_index('ix_request_logs_provider_request_id', table_name='request_logs')
    op.drop_column('request_logs', 'provider_request_id')
