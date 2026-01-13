"""add_detail_fields_to_request_logs

Revision ID: 5c7974e45bb3
Revises: 001
Create Date: 2026-01-13 10:56:28.063656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c7974e45bb3'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加详细字段到 request_logs 表
    op.add_column('request_logs', sa.Column('user_input_text', sa.Text(), nullable=True))
    op.add_column('request_logs', sa.Column('ai_response_text', sa.Text(), nullable=True))
    op.add_column('request_logs', sa.Column('temperature', sa.String(50), nullable=True))
    op.add_column('request_logs', sa.Column('top_p', sa.String(50), nullable=True))
    op.add_column('request_logs', sa.Column('top_k', sa.String(50), nullable=True))
    op.add_column('request_logs', sa.Column('max_tokens', sa.Integer(), nullable=True))
    op.add_column('request_logs', sa.Column('frequency_penalty', sa.String(50), nullable=True))
    op.add_column('request_logs', sa.Column('presence_penalty', sa.String(50), nullable=True))
    op.add_column('request_logs', sa.Column('stream', sa.String(10), nullable=True))


def downgrade() -> None:
    # 删除字段
    op.drop_column('request_logs', 'stream')
    op.drop_column('request_logs', 'presence_penalty')
    op.drop_column('request_logs', 'frequency_penalty')
    op.drop_column('request_logs', 'max_tokens')
    op.drop_column('request_logs', 'top_k')
    op.drop_column('request_logs', 'top_p')
    op.drop_column('request_logs', 'temperature')
    op.drop_column('request_logs', 'ai_response_text')
    op.drop_column('request_logs', 'user_input_text')
