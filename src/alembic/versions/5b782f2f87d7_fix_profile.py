"""fix profile

Revision ID: 5b782f2f87d7
Revises: e9ff2b7a0950
Create Date: 2023-09-09 18:03:59.542197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b782f2f87d7'
down_revision = 'e9ff2b7a0950'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_server_access_url_uc', 'profile', type_='unique')
    op.create_unique_constraint('_server_key_uc', 'profile', ['server_id', 'key_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_server_key_uc', 'profile', type_='unique')
    op.create_unique_constraint('_server_access_url_uc', 'profile', ['server_id', 'access_url'])
    # ### end Alembic commands ###
