"""upgrade payment table add field payment_type_id

Revision ID: 6eb6b72fe2f1
Revises: baef9a0bd089
Create Date: 2023-12-18 19:10:47.498117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6eb6b72fe2f1"
down_revision = "baef9a0bd089"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "payment", sa.Column("payment_type_id", sa.Integer(), nullable=True)
    )
    op.drop_constraint("payment_status_id_fkey", "payment", type_="foreignkey")
    op.create_foreign_key(
        None,
        "payment",
        "status",
        ["status_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        None,
        "payment",
        "payment_type",
        ["payment_type_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "payment", type_="foreignkey")
    op.drop_constraint(None, "payment", type_="foreignkey")
    op.create_foreign_key(
        "payment_status_id_fkey",
        "payment",
        "status",
        ["status_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("payment", "payment_type_id")
    # ### end Alembic commands ###
