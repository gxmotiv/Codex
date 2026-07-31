"""initial chart storage tables

Revision ID: 0001_initial_tables
Revises:
Create Date: 2026-05-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_charts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("birth_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.String(length=64), nullable=False),
        sa.Column("longitude", sa.String(length=64), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("chart_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_saved_charts_name", "saved_charts", ["name"])
    op.create_index("ix_saved_charts_birth_datetime", "saved_charts", ["birth_datetime"])

    op.create_table(
        "user_queries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("chart_id", sa.String(length=36), sa.ForeignKey("saved_charts.id"), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("context_payload", sa.JSON(), nullable=False),
        sa.Column("prediction_payload", sa.JSON(), nullable=False),
        sa.Column("llm_provider", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "golden_validation_charts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("label", sa.String(length=255), nullable=False, unique=True),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("expected_payload", sa.JSON(), nullable=False),
        sa.Column("tolerance_payload", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_golden_validation_charts_label", "golden_validation_charts", ["label"])


def downgrade() -> None:
    op.drop_index("ix_golden_validation_charts_label", table_name="golden_validation_charts")
    op.drop_table("golden_validation_charts")
    op.drop_table("user_queries")
    op.drop_index("ix_saved_charts_birth_datetime", table_name="saved_charts")
    op.drop_index("ix_saved_charts_name", table_name="saved_charts")
    op.drop_table("saved_charts")
