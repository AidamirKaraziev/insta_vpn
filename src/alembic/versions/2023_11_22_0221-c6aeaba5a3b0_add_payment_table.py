"""add payment table

Revision ID: c6aeaba5a3b0
Revises: d6c9f51a1f8e
Create Date: 2023-11-22 02:21:07.176440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c6aeaba5a3b0"
down_revision = "d6c9f51a1f8e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "payment",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("referent_id", sa.UUID(), nullable=True),
        sa.Column("sum", sa.Integer(), nullable=True),
        sa.Column("spb_number", sa.String(), nullable=True),
        sa.Column("card_number", sa.String(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("status_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["referent_id"], ["referent.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["status_id"], ["status.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("payment")
    # ### end Alembic commands ###
