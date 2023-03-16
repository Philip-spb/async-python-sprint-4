"""02_add_short_link_model

Revision ID: 58d876a05253
Revises: 3179149a5337
Create Date: 2023-03-15 02:39:41.458976

"""
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58d876a05253'
down_revision = '3179149a5337'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('short_link',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('short_url', sa.String(length=100), nullable=False),
    sa.Column('original_url', sa.String(length=4096), nullable=False),
    sa.Column('type', sa.String(length=100), server_default='public', nullable=False),
    sa.Column('owner_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='True', nullable=True),
    sa.Column('create_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('original_url'),
    sa.UniqueConstraint('short_url')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('short_link')
    # ### end Alembic commands ###
