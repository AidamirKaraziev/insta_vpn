"""add referral and partner

Revision ID: d0c5a572b232
Revises: c3b0441d6b14
Create Date: 2023-10-27 22:51:40.591287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d0c5a572b232"
down_revision = "c3b0441d6b14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "partner",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("number", sa.String(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "referral",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("partner_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("referral_link", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["partner_id"], ["partner.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("account", sa.Column("trial", sa.Boolean(), nullable=True))
    op.add_column(
        "account", sa.Column("referral_id", sa.UUID(), nullable=True)
    )
    op.create_foreign_key(
        None,
        "account",
        "referral",
        ["referral_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "account", type_="foreignkey")
    op.drop_column("account", "referral_id")
    op.drop_column("account", "trial")
    op.drop_table("referral")
    op.drop_table("partner")
    # ### end Alembic commands ###