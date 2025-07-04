"""Update lesson table to sync with frontend

Revision ID: ac5acc66cadc
Revises: 08cea36964bf
Create Date: 2025-07-05 01:54:47.857843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac5acc66cadc'
down_revision: Union[str, None] = '08cea36964bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lesson_attachments', sa.Column('url', sa.String(length=500), nullable=False))
    op.drop_column('lesson_attachments', 'file_url')
    op.add_column('lessons', sa.Column('instructor', sa.String(length=255), nullable=True))
    op.drop_column('lessons', 'instructor_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lessons', sa.Column('instructor_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('lessons', 'instructor')
    op.add_column('lesson_attachments', sa.Column('file_url', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.drop_column('lesson_attachments', 'url')
    # ### end Alembic commands ###
