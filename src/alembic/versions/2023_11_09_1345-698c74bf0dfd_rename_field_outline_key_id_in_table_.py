"""rename field outline_key_id in table Profile

Revision ID: 698c74bf0dfd
Revises: 6b7b789640a5
Create Date: 2023-11-09 13:45:14.316384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "698c74bf0dfd"
down_revision = "6b7b789640a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "profile", sa.Column("outline_key_id", sa.BigInteger(), nullable=True)
    )
    op.drop_constraint(
        "profile_shadowsocks_key_id_key", "profile", type_="unique"
    )
    op.create_unique_constraint(None, "profile", ["outline_key_id"])
    op.drop_constraint(
        "profile_shadowsocks_key_id_fkey", "profile", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "profile",
        "outline_key",
        ["outline_key_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("profile", "shadowsocks_key_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "profile",
        sa.Column(
            "shadowsocks_key_id",
            sa.BIGINT(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(None, "profile", type_="foreignkey")
    op.create_foreign_key(
        "profile_shadowsocks_key_id_fkey",
        "profile",
        "outline_key",
        ["shadowsocks_key_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(None, "profile", type_="unique")
    op.create_unique_constraint(
        "profile_shadowsocks_key_id_key", "profile", ["shadowsocks_key_id"]
    )
    op.drop_column("profile", "outline_key_id")
    # ### end Alembic commands ###
