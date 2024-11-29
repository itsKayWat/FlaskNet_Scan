"""initial migration

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(64), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('password_hash', sa.String(128)),
        sa.Column('role', sa.String(20), default='user'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Create servers table
    op.create_table(
        'server',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('host', sa.String(120), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), default='stopped'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('last_active', sa.DateTime()),
        sa.Column('owner_id', sa.Integer()),
        sa.Column('is_ssl_enabled', sa.Boolean(), default=False),
        sa.Column('ssl_cert_path', sa.String(256)),
        sa.Column('ssl_key_path', sa.String(256)),
        sa.Column('auto_restart', sa.Boolean(), default=False),
        sa.Column('debug_mode', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'])
    )

    # Create server_logs table
    op.create_table(
        'server_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('server_id', sa.Integer()),
        sa.Column('level', sa.String(20)),
        sa.Column('message', sa.Text()),
        sa.Column('timestamp', sa.DateTime()),
        sa.Column('category', sa.String(50)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['server_id'], ['server.id'])
    )

    # Create activity_logs table
    op.create_table(
        'activity_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('action', sa.String(100)),
        sa.Column('details', sa.Text()),
        sa.Column('timestamp', sa.DateTime()),
        sa.Column('ip_address', sa.String(45)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'])
    )

def downgrade():
    op.drop_table('activity_log')
    op.drop_table('server_log')
    op.drop_table('server')
    op.drop_table('user')