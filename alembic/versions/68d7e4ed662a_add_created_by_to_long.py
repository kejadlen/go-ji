"""Add created_by to long

Revision ID: 68d7e4ed662a
Revises: bf7c50886b7d
Create Date: 2024-02-15 08:31:57.799981

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "68d7e4ed662a"
down_revision: Union[str, None] = "bf7c50886b7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("longs") as batch_op:
        batch_op.add_column(sa.Column("created_by_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            op.f("fk_longs_created_by_id_users"),
            "users",
            ["created_by_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("longs") as batch_op:
        batch_op.drop_constraint(
            op.f("fk_longs_created_by_id_users"), type_="foreignkey"
        )
        batch_op.drop_column("created_by_id")
