"""add server to vless_key

Revision ID: 932ca11a5514
Revises: 62f9c3db5f57
Create Date: 2023-11-03 00:11:13.493723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "932ca11a5514"
down_revision = "62f9c3db5f57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "server", sa.Column("vpn_type_id", sa.Integer(), nullable=True)
    )
    op.alter_column(
        "server", "api_url", existing_type=sa.VARCHAR(), nullable=True
    )
    op.create_foreign_key(
        None,
        "server",
        "vpn_type",
        ["vpn_type_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "vless_key", sa.Column("server_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "vless_key", "server", ["server_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_column("vless_key", "server_ip")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "vless_key",
        sa.Column(
            "server_ip", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(None, "vless_key", type_="foreignkey")
    op.drop_column("vless_key", "server_id")
    op.drop_constraint(None, "server", type_="foreignkey")
    op.alter_column(
        "server", "api_url", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("server", "vpn_type_id")
    # ### end Alembic commands ###