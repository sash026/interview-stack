"""rework_interview_status_state_machine

Revision ID: 4df3e2474ceb
Revises: f3315afe77e6
Create Date: 2026-07-07 14:33:22.044332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4df3e2474ceb'
down_revision: Union[str, None] = 'f3315afe77e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("failure_reason", sa.Text(), nullable=True))

    # Collapse the 5-state machine (pending/transcribing/processing/
    # completed/failed) down to 4 states (uploaded/processing/completed/
    # failed). Postgres enums can't have values removed or renamed
    # in-place, so this recreates the type and remaps existing rows.
    op.execute("ALTER TYPE interview_status RENAME TO interview_status_old")
    op.execute(
        "CREATE TYPE interview_status AS ENUM "
        "('uploaded', 'processing', 'completed', 'failed')"
    )
    op.execute(
        """
        ALTER TABLE interviews
        ALTER COLUMN status TYPE interview_status
        USING (
            CASE status::text
                WHEN 'pending' THEN 'uploaded'
                WHEN 'transcribing' THEN 'processing'
                WHEN 'processing' THEN 'processing'
                WHEN 'completed' THEN 'completed'
                WHEN 'failed' THEN 'failed'
            END
        )::interview_status
        """
    )
    op.execute("DROP TYPE interview_status_old")


def downgrade() -> None:
    op.execute("ALTER TYPE interview_status RENAME TO interview_status_new")
    op.execute(
        "CREATE TYPE interview_status AS ENUM "
        "('pending', 'transcribing', 'processing', 'completed', 'failed')"
    )
    op.execute(
        """
        ALTER TABLE interviews
        ALTER COLUMN status TYPE interview_status
        USING (
            CASE status::text
                WHEN 'uploaded' THEN 'pending'
                WHEN 'processing' THEN 'processing'
                WHEN 'completed' THEN 'completed'
                WHEN 'failed' THEN 'failed'
            END
        )::interview_status
        """
    )
    op.execute("DROP TYPE interview_status_new")

    op.drop_column("interviews", "failure_reason")
