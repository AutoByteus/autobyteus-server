"""create conversation models for workflow step

Revision ID: 49afb9deb4cd
Revises: 
Create Date: 2024-11-05 20:38:27.871901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49afb9deb4cd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('step_conversations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('step_conversation_id', sa.String(length=36), nullable=False),
    sa.Column('step_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('step_conversation_id')
    )
    op.create_table('step_conversation_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('step_conversation_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('original_message', sa.Text(), nullable=True),
    sa.Column('context_paths', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['step_conversation_id'], ['step_conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('step_conversation_messages')
    op.drop_table('step_conversations')
    # ### end Alembic commands ###
