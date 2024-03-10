"""Add users table

Revision ID: 547284b1a771
Revises: 
Create Date: 2022-12-11 16:46:13.323008

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '547284b1a771'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_on', sa.DateTime(), nullable=False),
                    sa.Column('updated_on', sa.DateTime(), nullable=True),
                    sa.Column('is_deleted', sa.Boolean(), nullable=False),
                    sa.Column('first_name', sa.String(), nullable=True),
                    sa.Column('middle_name', sa.String(), nullable=True),
                    sa.Column('last_name', sa.String(), nullable=True),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('phone_number', sa.String(), nullable=True),
                    sa.Column('password_hash', sa.LargeBinary(), nullable=False),
                    sa.Column('password_salt', sa.LargeBinary(), nullable=False),
                    sa.Column('is_admin', sa.Boolean(), nullable=False),
                    sa.Column('is_staff', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
