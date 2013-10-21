from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
picture = Table('picture', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('url', String),
    Column('book', Integer),
)

picture = Table('picture', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('url', String(length=140)),
    Column('book_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['picture'].columns['book'].drop()
    post_meta.tables['picture'].columns['book_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['picture'].columns['book'].create()
    post_meta.tables['picture'].columns['book_id'].drop()
