"""add status

Revision ID: d6c9f51a1f8e
Revises: da367074eb8e
Create Date: 2023-11-22 01:45:10.027332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d6c9f51a1f8e"
down_revision = "da367074eb8e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("status")
    # ### end Alembic commands ###