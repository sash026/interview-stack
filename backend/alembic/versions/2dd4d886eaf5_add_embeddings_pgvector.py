"""add_embeddings_pgvector

Revision ID: 2dd4d886eaf5
Revises: 6c963d2b735b
Create Date: 2026-07-07 15:50:26.195460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from app.core.config import settings


# revision identifiers, used by Alembic.
revision: str = '2dd4d886eaf5'
down_revision: Union[str, None] = '6c963d2b735b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "embeddings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("interview_id", sa.UUID(), nullable=False),
        sa.Column("vector", Vector(settings.EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("interview_id"),
    )

    # HNSW over IVFFlat: HNSW builds incrementally with no training step, so
    # it works correctly on a table that starts empty and grows one row at a
    # time as interviews complete. IVFFlat's clusters are computed from
    # whatever data exists at CREATE INDEX time, so it degrades badly (or
    # needs periodic REINDEX) under exactly that access pattern. Cosine ops
    # match how embedding models like text-embedding-3-small are meant to be
    # compared.
    op.execute(
        "CREATE INDEX embeddings_vector_hnsw_idx ON embeddings "
        "USING hnsw (vector vector_cosine_ops)"
    )
    # The UniqueConstraint above already gives interview_id a b-tree index,
    # which is what both enforces "one embedding per interview" and makes
    # store_embedding's upsert lookup fast - no separate index needed.


def downgrade() -> None:
    op.drop_index("embeddings_vector_hnsw_idx", table_name="embeddings")
    op.drop_table("embeddings")
    op.execute("DROP EXTENSION IF EXISTS vector")
