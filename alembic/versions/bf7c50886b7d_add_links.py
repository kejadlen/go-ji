"""Add links

Revision ID: bf7c50886b7d
Revises: 006936f7f7f1
Create Date: 2024-02-14 16:16:17.446273

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf7c50886b7d"
down_revision: str | None = "006936f7f7f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shorts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shorts")),
        sa.UniqueConstraint("slug", name=op.f("uq_shorts_slug")),
    )
    op.create_table(
        "longs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("short_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["short_id"], ["shorts.id"], name=op.f("fk_longs_short_id_shorts")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_longs")),
    )


def downgrade() -> None:
    op.drop_table("longs")
    op.drop_table("shorts")
