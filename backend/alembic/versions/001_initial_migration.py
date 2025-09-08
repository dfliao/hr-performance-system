"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-09-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('code', sa.String(length=20), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
        sa.Column('path', sa.String(length=255), nullable=True),
        sa.Column('manager_user_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id']),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ldap_uid', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True, index=True),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('employee_id', sa.String(length=20), nullable=True, index=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended'), nullable=False, default='active'),
        sa.Column('role', sa.Enum('admin', 'auditor', 'manager', 'employee'), nullable=False, default='employee'),
        sa.Column('last_ldap_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ldap_dn', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
    )
    
    # Add foreign key for department manager
    op.create_foreign_key(
        'fk_departments_manager_user_id', 'departments', 'users',
        ['manager_user_id'], ['id']
    )
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('redmine_project_id', sa.Integer(), nullable=True, index=True),
        sa.Column('redmine_identifier', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'completed', 'archived'), nullable=False, default='active'),
        sa.Column('priority', sa.Integer(), nullable=False, default=1),
        sa.Column('manager_user_id', sa.Integer(), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('enable_performance_tracking', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['manager_user_id'], ['users.id']),
    )
    
    # Create rule_packs table
    op.create_table(
        'rule_packs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=False, default='1.0.0'),
        sa.Column('scope', sa.Enum('company', 'department', 'role'), nullable=False, default='company'),
        sa.Column('target_department_id', sa.Integer(), nullable=True),
        sa.Column('target_role', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'inactive', 'archived'), nullable=False, default='draft'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('json_schema', sa.JSON(), nullable=True),
        sa.Column('weight_config', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['target_department_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
    )
    
    # Create rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_pack_id', sa.Integer(), nullable=False, index=True),
        sa.Column('code', sa.String(length=50), nullable=False, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('direction', sa.Enum('positive', 'negative'), nullable=False, default='positive'),
        sa.Column('base_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('weight', sa.Float(), nullable=False, default=1.0),
        sa.Column('caps', sa.Float(), nullable=True),
        sa.Column('min_score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=True),
        sa.Column('evidence_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('manager_approval_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rule_pack_id'], ['rule_packs.id']),
    )
    
    # Create periods table
    op.create_table(
        'periods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('monthly', 'quarterly', 'yearly'), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('month', sa.Integer(), nullable=True, index=True),
        sa.Column('quarter', sa.Integer(), nullable=True, index=True),
        sa.Column('start_date', sa.Date(), nullable=False, index=True),
        sa.Column('end_date', sa.Date(), nullable=False, index=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('locked_by', sa.Integer(), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['locked_by'], ['users.id']),
    )
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('reporter_id', sa.Integer(), nullable=False, index=True),
        sa.Column('department_id', sa.Integer(), nullable=True, index=True),
        sa.Column('project_id', sa.Integer(), nullable=True, index=True),
        sa.Column('rule_id', sa.Integer(), nullable=False, index=True),
        sa.Column('original_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('adjusted_score', sa.Float(), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('adjustment_reason', sa.Text(), nullable=True),
        sa.Column('occurred_at', sa.Date(), nullable=False, index=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('evidence_urls', sa.JSON(), nullable=True),
        sa.Column('evidence_count', sa.Integer(), nullable=False, default=0),
        sa.Column('source', sa.Enum('manual', 'redmine', 'n8n', 'note', 'api'), nullable=False, default='manual'),
        sa.Column('external_id', sa.String(length=100), nullable=True, index=True),
        sa.Column('source_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'pending', 'approved', 'rejected', 'archived'), nullable=False, default='pending'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('period_year', sa.Integer(), nullable=False, index=True),
        sa.Column('period_month', sa.Integer(), nullable=False, index=True),
        sa.Column('period_quarter', sa.Integer(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
    )
    
    # Create scores table
    op.create_table(
        'scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('period_id', sa.Integer(), nullable=False, index=True),
        sa.Column('period_year', sa.Integer(), nullable=False, index=True),
        sa.Column('period_month', sa.Integer(), nullable=True, index=True),
        sa.Column('period_quarter', sa.Integer(), nullable=True, index=True),
        sa.Column('period_type', sa.String(length=20), nullable=False, index=True),
        sa.Column('department_id', sa.Integer(), nullable=True, index=True),
        sa.Column('total_score', sa.Float(), nullable=False, default=0.0, index=True),
        sa.Column('positive_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('negative_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('adjusted_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_events', sa.Integer(), nullable=False, default=0),
        sa.Column('positive_events', sa.Integer(), nullable=False, default=0),
        sa.Column('negative_events', sa.Integer(), nullable=False, default=0),
        sa.Column('pending_events', sa.Integer(), nullable=False, default=0),
        sa.Column('rule_breakdown', sa.JSON(), nullable=True),
        sa.Column('rank_department', sa.Integer(), nullable=True, index=True),
        sa.Column('rank_company', sa.Integer(), nullable=True, index=True),
        sa.Column('percentile_department', sa.Float(), nullable=True),
        sa.Column('percentile_company', sa.Float(), nullable=True),
        sa.Column('previous_total_score', sa.Float(), nullable=True),
        sa.Column('score_change', sa.Float(), nullable=True),
        sa.Column('score_change_percent', sa.Float(), nullable=True),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('events_computed_count', sa.Integer(), nullable=False, default=0),
        sa.Column('computation_version', sa.String(length=10), nullable=False, default='1.0'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, default=False),
        sa.Column('has_adjustments', sa.Boolean(), nullable=False, default=False),
        sa.Column('needs_recalculation', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['period_id'], ['periods.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.UniqueConstraint('user_id', 'period_id', name='uq_user_period'),
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True, index=True),
        sa.Column('actor_username', sa.String(length=50), nullable=True),
        sa.Column('actor_ip', sa.String(length=45), nullable=True),
        sa.Column('actor_user_agent', sa.String(length=500), nullable=True),
        sa.Column('action', sa.Enum('create', 'read', 'update', 'delete', 'login', 'logout', 'approve', 'reject', 'export', 'import', 'lock', 'unlock', 'calculate'), nullable=False, index=True),
        sa.Column('entity_type', sa.Enum('user', 'department', 'project', 'rule_pack', 'rule', 'event', 'period', 'score', 'report', 'file', 'system'), nullable=False, index=True),
        sa.Column('entity_id', sa.Integer(), nullable=True, index=True),
        sa.Column('entity_name', sa.String(length=200), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('diff', sa.JSON(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=50), nullable=True, index=True),
        sa.Column('session_id', sa.String(length=100), nullable=True, index=True),
        sa.Column('success', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=False, default=0),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, default=False, index=True),
        sa.Column('requires_review', sa.Boolean(), nullable=False, default=False, index=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
    )
    
    # Create indexes for performance
    op.create_index('ix_events_occurred_at_user', 'events', ['occurred_at', 'user_id'])
    op.create_index('ix_events_status_department', 'events', ['status', 'department_id'])
    op.create_index('ix_scores_period_department', 'scores', ['period_year', 'period_month', 'department_id'])
    op.create_index('ix_audit_logs_timestamp_actor', 'audit_logs', ['timestamp', 'actor_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_audit_logs_timestamp_actor', 'audit_logs')
    op.drop_index('ix_scores_period_department', 'scores')
    op.drop_index('ix_events_status_department', 'events')
    op.drop_index('ix_events_occurred_at_user', 'events')
    
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('scores')
    op.drop_table('events')
    op.drop_table('periods')
    op.drop_table('rules')
    op.drop_table('rule_packs')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('departments')