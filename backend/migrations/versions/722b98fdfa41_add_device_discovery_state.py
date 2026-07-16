"""Add device discovery state

Revision ID: 722b98fdfa41
Revises: af24f0e0b602
Create Date: 2026-07-16 21:56:14.529126

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "722b98fdfa41"
down_revision: Union[str, Sequence[str], None] = "af24f0e0b602"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add discovery-state tracking columns to devices.

    Existing devices receive a missed-scan count of zero.
    The temporary database-level default is removed after the
    column has been populated.
    """

    with op.batch_alter_table("devices") as batch_op:
        batch_op.add_column(
            sa.Column(
                "last_discovery_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "consecutive_missed_scans",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            )
        )

    # Keep default handling in the SQLAlchemy application model
    # rather than permanently defining it at database level.
    with op.batch_alter_table("devices") as batch_op:
        batch_op.alter_column(
            "consecutive_missed_scans",
            server_default=None,
        )


def downgrade() -> None:
    """
    Remove discovery-state tracking columns from devices.
    """

    with op.batch_alter_table("devices") as batch_op:
        batch_op.drop_column("consecutive_missed_scans")
        batch_op.drop_column("last_discovery_at")
