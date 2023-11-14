"""remove field dynamic_key in table Profile

Revision ID: da05abd99202
Revises: 5a14e6bfdd8c
Create Date: 2023-11-11 17:32:01.133675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da05abd99202"
down_revision = "5a14e6bfdd8c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("profile_dynamic_key_key", "profile", type_="unique")
    op.drop_column("profile", "dynamic_key")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "profile",
        sa.Column(
            "dynamic_key", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.create_unique_constraint(
        "profile_dynamic_key_key", "profile", ["dynamic_key"]
    )
    # ### end Alembic commands ###
