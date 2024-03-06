"""Include name for users

Revision ID: da9477cfcdeb
Revises: a4f240bbc8f9
Create Date: 2024-02-15 12:49:41.333839

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "da9477cfcdeb"
down_revision: str | None = "a4f240bbc8f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.Text()))
    op.execute('UPDATE users SET name = "" WHERE name IS NULL')
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("name", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "name")
