"""update_tariff+photo_url

Revision ID: e9ff2b7a0950
Revises: e06004c345c7
Create Date: 2023-09-09 12:40:58.357283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9ff2b7a0950'
down_revision = 'e06004c345c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tariff', sa.Column('photo_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tariff', 'photo_url')
    # ### end Alembic commands ###