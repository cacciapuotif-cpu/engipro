"""Registro audit con protezione append-only anche per SQL diretto."""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(10), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('path', sa.String(2048), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(512), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    )
    for column in ('user_id', 'resource_type', 'timestamp'):
        op.create_index(f'ix_audit_logs_{column}', 'audit_logs', [column])
    dialect = op.get_bind().dialect.name
    if dialect == 'sqlite':
        for action in ('UPDATE', 'DELETE'):
            op.execute(f"CREATE TRIGGER audit_no_{action.lower()} BEFORE {action} ON audit_logs BEGIN SELECT RAISE(ABORT, 'Audit immutabile'); END")
    elif dialect == 'postgresql':
        op.execute("CREATE FUNCTION reject_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Audit immutabile'; END; $$")
        op.execute('CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON audit_logs FOR EACH STATEMENT EXECUTE FUNCTION reject_audit_mutation()')


def downgrade() -> None:
    op.drop_table('audit_logs')
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('DROP FUNCTION reject_audit_mutation()')
