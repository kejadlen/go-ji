"""Add click count

Revision ID: a4f240bbc8f9
Revises: 68d7e4ed662a
Create Date: 2024-02-15 08:37:31.433274

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4f240bbc8f9"
down_revision: str | None = "68d7e4ed662a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("shorts", sa.Column("clicks", sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column("shorts", "clicks")
