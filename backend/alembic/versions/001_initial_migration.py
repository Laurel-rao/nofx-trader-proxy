"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 provider_configs 表
    op.create_table(
        'provider_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('api_base_url', sa.String(500), nullable=False),
        sa.Column('api_key', sa.String(500), nullable=False),
        sa.Column('default_model', sa.String(100), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_provider_configs_name', 'provider_configs', ['name'])
    op.create_index('ix_provider_configs_is_enabled', 'provider_configs', ['is_enabled'])
    op.create_index('ix_provider_configs_priority', 'provider_configs', ['priority'])

    # 创建 request_logs 表
    op.create_table(
        'request_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('request_id', sa.String(255), nullable=False, unique=True),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('request_params', postgresql.JSONB, nullable=False),
        sa.Column('response_content', postgresql.JSONB, nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('duration_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status_code', sa.Integer(), nullable=False, server_default='200'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(255), nullable=True),
    )
    op.create_index('ix_request_logs_request_id', 'request_logs', ['request_id'])
    op.create_index('ix_request_logs_provider', 'request_logs', ['provider'])
    op.create_index('ix_request_logs_model', 'request_logs', ['model'])
    op.create_index('ix_request_logs_user_id', 'request_logs', ['user_id'])
    op.create_index('ix_request_logs_created_at', 'request_logs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_request_logs_created_at', table_name='request_logs')
    op.drop_index('ix_request_logs_user_id', table_name='request_logs')
    op.drop_index('ix_request_logs_model', table_name='request_logs')
    op.drop_index('ix_request_logs_provider', table_name='request_logs')
    op.drop_index('ix_request_logs_request_id', table_name='request_logs')
    op.drop_table('request_logs')
    
    op.drop_index('ix_provider_configs_priority', table_name='provider_configs')
    op.drop_index('ix_provider_configs_is_enabled', table_name='provider_configs')
    op.drop_index('ix_provider_configs_name', table_name='provider_configs')
    op.drop_table('provider_configs')

