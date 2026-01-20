"""
Initial schema migration - Create User, Task, Conversation, Message tables

Revision ID: 001
"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op

# Alembic metadata
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema"""

    # Create users table
    op.create_table(
        "user",
        sa.Column("user_id", sa.VARCHAR(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_user_user_id", "user", ["user_id"])

    # Create tasks table
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.VARCHAR(255), nullable=False),
        sa.Column("title", sa.VARCHAR(1000), nullable=False),
        sa.Column("description", sa.VARCHAR(1000), nullable=True),
        sa.Column(
            "completed", sa.Boolean(), nullable=False, server_default=sa.literal(False)
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_user_id", "task", ["user_id"])
    op.create_index("ix_task_title", "task", ["title"])
    op.create_index("ix_task_completed", "task", ["completed"])

    # Create conversations table
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.VARCHAR(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_user_id", "conversation", ["user_id"])

    # Create messages table
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.VARCHAR(255), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.VARCHAR(20), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversation.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_message_user_id", "message", ["user_id"])
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])
    op.create_index("ix_message_role", "message", ["role"])


def downgrade() -> None:
    """Downgrade database schema"""
    op.drop_index("ix_message_role", table_name="message")
    op.drop_index("ix_message_conversation_id", table_name="message")
    op.drop_index("ix_message_user_id", table_name="message")
    op.drop_table("message")

    op.drop_index("ix_conversation_user_id", table_name="conversation")
    op.drop_table("conversation")

    op.drop_index("ix_task_completed", table_name="task")
    op.drop_index("ix_task_title", table_name="task")
    op.drop_index("ix_task_user_id", table_name="task")
    op.drop_table("task")

    op.drop_index("ix_user_user_id", table_name="user")
    op.drop_table("user")
