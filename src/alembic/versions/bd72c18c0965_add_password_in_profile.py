"""add password in profile

Revision ID: bd72c18c0965
Revises: f6cf658eabd3
Create Date: 2023-10-14 16:21:28.659299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd72c18c0965'
down_revision = 'f6cf658eabd3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile', sa.Column('password', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profile', 'password')
    # ### end Alembic commands ###
