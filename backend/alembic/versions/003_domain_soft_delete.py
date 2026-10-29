"""Soft delete per aziende, scadenze e partecipazioni preesistenti."""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ('companies', 'deadlines', 'course_participations'):
        op.add_column(table, sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    for table in ('course_participations', 'deadlines', 'companies'):
        with op.batch_alter_table(table) as batch:
            batch.drop_column('is_active')
