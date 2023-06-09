"""06_fix_short_link_type_param

Revision ID: 2d94b2cb61b4
Revises: 947ec694e83d
Create Date: 2023-03-20 22:35:46.857997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d94b2cb61b4'
down_revision = '947ec694e83d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('short_link', sa.Column('link_type', sa.String(length=100), server_default='public', nullable=False))
    op.drop_column('short_link', 'type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('short_link', sa.Column('type', sa.VARCHAR(length=100), server_default=sa.text("'public'::character varying"), autoincrement=False, nullable=False))
    op.drop_column('short_link', 'link_type')
    # ### end Alembic commands ###
