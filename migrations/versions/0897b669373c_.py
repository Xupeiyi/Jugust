"""empty message

Revision ID: 0897b669373c
Revises: 4bb9020d4357
Create Date: 2019-08-12 22:51:07.139041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0897b669373c'
down_revision = '4bb9020d4357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collect',
    sa.Column('collector_id', sa.Integer(), nullable=False),
    sa.Column('collected_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['collected_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['collector_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('collector_id', 'collected_id')
    )
    op.create_index(op.f('ix_collect_timestamp'), 'collect', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_collect_timestamp'), table_name='collect')
    op.drop_table('collect')
    # ### end Alembic commands ###
