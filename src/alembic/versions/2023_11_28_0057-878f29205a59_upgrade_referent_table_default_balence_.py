"""upgrade referent table default balence is 0

Revision ID: 878f29205a59
Revises: 041491198d9c
Create Date: 2023-11-28 00:57:03.560467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "878f29205a59"
down_revision = "041491198d9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
