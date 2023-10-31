"""update account rename trial_is_active

Revision ID: 1402e2c1d585
Revises: e9249795677f
Create Date: 2023-10-28 13:47:18.903035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1402e2c1d585"
down_revision = "e9249795677f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "account", sa.Column("trial_is_active", sa.Boolean(), nullable=True)
    )
    op.drop_column("account", "trial_was_used")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "account",
        sa.Column(
            "trial_was_used", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("account", "trial_is_active")
    # ### end Alembic commands ###
