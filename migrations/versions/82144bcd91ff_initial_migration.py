"""Initial migration

Revision ID: 82144bcd91ff
Revises: 
Create Date: 2024-06-28 18:18:12.395769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82144bcd91ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('membership', sa.Enum('FREE', 'PREMIUM', 'VIP', name='membership_types'), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'BANNED', name='status_types'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('word_count', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=True),
    sa.Column('url', sa.String(length=500), nullable=True),
    sa.Column('site', sa.String(length=100), nullable=True),
    sa.Column('site_name', sa.String(length=100), nullable=True),
    sa.Column('site_icon', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_article_site'), ['site'], unique=False)
        batch_op.create_index(batch_op.f('ix_article_url'), ['url'], unique=False)

    op.create_table('paragraph',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unfamiliar_word',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=100), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('paragraph_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['paragraph_id'], ['paragraph.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unfamiliar_word')
    op.drop_table('paragraph')
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_url'))
        batch_op.drop_index(batch_op.f('ix_article_site'))

    op.drop_table('article')
    op.drop_table('user')
    # ### end Alembic commands ###