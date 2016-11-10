"""empty message

Revision ID: 31d8495be9b6
Revises: None
Create Date: 2016-11-07 14:22:20.914790

"""

# revision identifiers, used by Alembic.
revision = '31d8495be9b6'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_for_html', sa.String(length=50), nullable=False),
    sa.Column('category_for_humans', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contacts',
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('first_name', sa.String(length=20), nullable=False),
    sa.Column('last_name', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('username')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('price', sa.String(length=50), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=False),
    sa.Column('completed', sa.Boolean(), nullable=False),
    sa.Column('expired', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['username'], ['contacts.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_categories')
    op.drop_table('posts')
    op.drop_table('contacts')
    op.drop_table('categories')
    ### end Alembic commands ###