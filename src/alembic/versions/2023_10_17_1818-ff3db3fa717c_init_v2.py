"""Init v2

Revision ID: ff3db3fa717c
Revises: bd72c18c0965
Create Date: 2023-10-17 18:18:47.926522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ff3db3fa717c"
down_revision = "bd72c18c0965"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "static_key",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=True),
        sa.Column("key_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(), nullable=True),
        sa.Column("access_url", sa.String(), nullable=True),
        sa.Column("used_bytes", sa.Integer(), nullable=True),
        sa.Column("data_limit", sa.Integer(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["server_id"], ["server.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "key_id", name="_key_server_uc"),
    )
    op.add_column(
        "profile", sa.Column("static_key_id", sa.BigInteger(), nullable=True)
    )
    op.drop_constraint("_server_key_uc", "profile", type_="unique")
    op.drop_constraint("profile_server_id_fkey", "profile", type_="foreignkey")
    op.create_foreign_key(
        None,
        "profile",
        "static_key",
        ["static_key_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("profile", "server_id")
    op.drop_column("profile", "password")
    op.drop_column("profile", "port")
    op.drop_column("profile", "key_id")
    op.drop_column("profile", "access_url")
    op.drop_column("profile", "data_limit")
    op.drop_column("profile", "method")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "profile",
        sa.Column("method", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "profile",
        sa.Column(
            "data_limit", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "profile",
        sa.Column(
            "access_url", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "profile",
        sa.Column("key_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "profile",
        sa.Column("port", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "profile",
        sa.Column(
            "password", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "profile",
        sa.Column(
            "server_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(None, "profile", type_="foreignkey")
    op.create_foreign_key(
        "profile_server_id_fkey",
        "profile",
        "server",
        ["server_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "_server_key_uc", "profile", ["server_id", "key_id"]
    )
    op.drop_column("profile", "static_key_id")
    op.drop_table("static_key")
    # ### end Alembic commands ###