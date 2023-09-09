"""update account 2

Revision ID: 434eef8234dc
Revises: 88368cada1d3
Create Date: 2023-09-06 14:35:12.740872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '434eef8234dc'
down_revision = '88368cada1d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('account_number_key', 'account', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('account_number_key', 'account', ['number'])
    # ### end Alembic commands ###