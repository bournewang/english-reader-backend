"""add currency to plan

Revision ID: b2cb747ed4cd
Revises: 8c4260356130
Create Date: 2024-06-28 18:37:17.201682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2cb747ed4cd'
down_revision = '8c4260356130'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.drop_column('currency')

    # ### end Alembic commands ###
