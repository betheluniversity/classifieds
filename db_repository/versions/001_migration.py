from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
contacts = Table('contacts', post_meta,
    Column('username', String(length=8), primary_key=True, nullable=False),
    Column('first_name', String(length=20), nullable=False),
    Column('last_name', String(length=30), nullable=False),
    Column('email', String(length=50), nullable=False),
    Column('phone_number', String(length=15), nullable=False),
    Column('isAdmin', Boolean, nullable=False, default=ColumnDefault(False)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contacts'].columns['isAdmin'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['contacts'].columns['isAdmin'].drop()
