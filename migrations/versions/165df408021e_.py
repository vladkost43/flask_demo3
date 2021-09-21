"""empty message

Revision ID: 165df408021e
Revises: b3aaa5a74b68
Create Date: 2021-09-21 18:30:13.407489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '165df408021e'
down_revision = 'b3aaa5a74b68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('event_artifact_event_id_fkey', 'event_artifact', type_='foreignkey')
    op.drop_constraint('event_artifact_artifact_id_fkey', 'event_artifact', type_='foreignkey')
    op.create_foreign_key(None, 'event_artifact', 'artifact', ['artifact_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'event_artifact', 'events', ['event_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('event_authors_event_id_fkey', 'event_authors', type_='foreignkey')
    op.drop_constraint('event_authors_authors_id_fkey', 'event_authors', type_='foreignkey')
    op.create_foreign_key(None, 'event_authors', 'authors', ['authors_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'event_authors', 'events', ['event_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('party_user_id_fkey', 'party', type_='foreignkey')
    op.drop_constraint('party_event_id_fkey', 'party', type_='foreignkey')
    op.create_foreign_key(None, 'party', 'events', ['event_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'party', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'party', type_='foreignkey')
    op.drop_constraint(None, 'party', type_='foreignkey')
    op.create_foreign_key('party_event_id_fkey', 'party', 'events', ['event_id'], ['id'])
    op.create_foreign_key('party_user_id_fkey', 'party', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'event_authors', type_='foreignkey')
    op.drop_constraint(None, 'event_authors', type_='foreignkey')
    op.create_foreign_key('event_authors_authors_id_fkey', 'event_authors', 'authors', ['authors_id'], ['id'])
    op.create_foreign_key('event_authors_event_id_fkey', 'event_authors', 'events', ['event_id'], ['id'])
    op.drop_constraint(None, 'event_artifact', type_='foreignkey')
    op.drop_constraint(None, 'event_artifact', type_='foreignkey')
    op.create_foreign_key('event_artifact_artifact_id_fkey', 'event_artifact', 'artifact', ['artifact_id'], ['id'])
    op.create_foreign_key('event_artifact_event_id_fkey', 'event_artifact', 'events', ['event_id'], ['id'])
    # ### end Alembic commands ###
