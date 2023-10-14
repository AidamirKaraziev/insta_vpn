"""add dynamic_key in profile

Revision ID: f6cf658eabd3
Revises: 3f75bb0945cf
Create Date: 2023-10-14 12:06:15.429215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6cf658eabd3'
down_revision = '3f75bb0945cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile', sa.Column('dynamic_key', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'profile', ['dynamic_key'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'profile', type_='unique')
    op.drop_column('profile', 'dynamic_key')
    # ### end Alembic commands ###
