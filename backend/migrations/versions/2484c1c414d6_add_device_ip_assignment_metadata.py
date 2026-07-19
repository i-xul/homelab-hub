"""Add device IP assignment metadata

Revision ID: 2484c1c414d6
Revises: 722b98fdfa41
Create Date: 2026-07-19 13:08:41.263019

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2484c1c414d6"
down_revision: Union[str, Sequence[str], None] = "722b98fdfa41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add user-managed IP assignment metadata to devices.

    Existing devices are initialized with an "unknown"
    assignment type so that the new non-nullable column can be
    added without losing inventory data.
    """

    with op.batch_alter_table("devices") as batch_op:
        batch_op.add_column(
            sa.Column(
                "ip_assignment",
                sa.String(length=20),
                nullable=False,
                server_default="unknown",
            )
        )

        batch_op.add_column(
            sa.Column(
                "expected_ip",
                sa.String(length=45),
                nullable=True,
            )
        )

    # Future default handling belongs to the SQLAlchemy model.
    # The temporary database default was needed only to migrate
    # rows that already existed.
    with op.batch_alter_table("devices") as batch_op:
        batch_op.alter_column(
            "ip_assignment",
            server_default=None,
        )


def downgrade() -> None:
    """
    Remove user-managed IP assignment metadata from devices.
    """

    with op.batch_alter_table("devices") as batch_op:
        batch_op.drop_column("expected_ip")
        batch_op.drop_column("ip_assignment")
