"""add_client_ip_to_request_logs

Revision ID: bbee7c1d716d
Revises: 37272603deda
Create Date: 2026-01-13 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bbee7c1d716d'
down_revision = '37272603deda'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加客户端 IP 字段到 request_logs 表
    op.add_column('request_logs', sa.Column('client_ip', sa.String(50), nullable=True))
    op.create_index('ix_request_logs_client_ip', 'request_logs', ['client_ip'])


def downgrade() -> None:
    # 删除索引和字段
    op.drop_index('ix_request_logs_client_ip', table_name='request_logs')
    op.drop_column('request_logs', 'client_ip')
