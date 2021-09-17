"""empty message

Revision ID: 660184f723b8
Revises: 31cb92f17304
Create Date: 2021-09-16 01:13:36.876389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '660184f723b8'
down_revision = '31cb92f17304'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('status', sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, 'events', ['status'])
    op.drop_column('events', 'status_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('status_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'events', type_='unique')
    op.drop_column('events', 'status')
    # ### end Alembic commands ###
