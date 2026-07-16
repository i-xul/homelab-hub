"""Create initial device inventory schema

Revision ID: af24f0e0b602
Revises:
Create Date: 2026-07-16 21:51:37.172328

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af24f0e0b602"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the initial HomeLab Hub inventory schema.

    This migration represents the database structure that
    existed before Alembic was introduced to the project.
    """

    op.create_table(
        "devices",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "mac_address",
            sa.String(length=17),
            nullable=False,
        ),
        sa.Column(
            "manufacturer",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "model",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "device_type",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "hostname",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "current_ip",
            sa.String(length=45),
            nullable=True,
        ),
        sa.Column(
            "online",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "friendly_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "trusted",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "pinned",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_devices_mac_address"),
        "devices",
        ["mac_address"],
        unique=True,
    )

    op.create_table(
        "device_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "session_start",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "session_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_device_sessions_device_id"),
        "device_sessions",
        ["device_id"],
        unique=False,
    )


def downgrade() -> None:
    """
    Remove the initial HomeLab Hub inventory schema.
    """

    op.drop_index(
        op.f("ix_device_sessions_device_id"),
        table_name="device_sessions",
    )
    op.drop_table("device_sessions")

    op.drop_index(
        op.f("ix_devices_mac_address"),
        table_name="devices",
    )
    op.drop_table("devices")
