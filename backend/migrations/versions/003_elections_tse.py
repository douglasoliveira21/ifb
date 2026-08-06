"""Elections and TSE integration tables

Revision ID: 003
Revises: 002
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Elections
    op.create_table(
        "elections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tse_election_id", sa.String(50), unique=True, index=True, nullable=True),
        sa.Column("year", sa.Integer, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("election_type", sa.String(50), index=True),
        sa.Column("scope", sa.String(50)),
        sa.Column("rounds", sa.Integer, server_default="1"),
        sa.Column("first_round_date", sa.Date, nullable=True),
        sa.Column("second_round_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), server_default="concluded"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Candidacies
    op.create_table(
        "candidacies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("politician_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("politicians.id"), nullable=True, index=True),
        sa.Column("election_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("elections.id"), index=True, nullable=False),
        sa.Column("tse_candidate_id", sa.String(50), index=True, nullable=True),
        sa.Column("sequence_number", sa.String(20), nullable=True),
        sa.Column("ballot_number", sa.String(10), nullable=True),
        sa.Column("ballot_name", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(500), nullable=False),
        sa.Column("cpf_hash", sa.String(128), nullable=True, index=True),
        sa.Column("party_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_parties.id"), nullable=True),
        sa.Column("position_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("political_positions.id"), nullable=True),
        sa.Column("state_code", sa.String(2), nullable=True, index=True),
        sa.Column("city_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(100), index=True, server_default="deferido"),
        sa.Column("status_detail", sa.String(255), nullable=True),
        sa.Column("reelection", sa.Boolean, server_default="false"),
        sa.Column("occupation", sa.String(255), nullable=True),
        sa.Column("education", sa.String(100), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("race_color", sa.String(50), nullable=True),
        sa.Column("marital_status", sa.String(50), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
        sa.Column("birth_place", sa.String(255), nullable=True),
        sa.Column("coalition_name", sa.String(500), nullable=True),
        sa.Column("coalition_parties", sa.Text, nullable=True),
        sa.Column("photo_url", sa.String(2048), nullable=True),
        sa.Column("reconciliation_status", sa.String(50), server_default="pending"),
        sa.Column("reconciliation_score", sa.Float, nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_candidacies_tse_election", "candidacies", ["tse_candidate_id", "election_id"], unique=True)

    # Candidate assets
    op.create_table(
        "candidate_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("category_code", sa.String(10), nullable=True),
        sa.Column("category_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("declared_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="BRL"),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Campaign revenues
    op.create_table(
        "campaign_revenues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("receipt_number", sa.String(50), nullable=True),
        sa.Column("donor_name", sa.String(500), nullable=True),
        sa.Column("donor_document_hash", sa.String(128), nullable=True),
        sa.Column("donor_type", sa.String(100), nullable=True),
        sa.Column("revenue_type", sa.String(100), nullable=True),
        sa.Column("resource_source", sa.String(255), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("received_at", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Campaign expenses
    op.create_table(
        "campaign_expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("supplier_name", sa.String(500), nullable=True),
        sa.Column("supplier_document_hash", sa.String(128), nullable=True),
        sa.Column("expense_type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("contracted_at", sa.Date, nullable=True),
        sa.Column("paid_at", sa.Date, nullable=True),
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Election results
    op.create_table(
        "election_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("round", sa.Integer, server_default="1"),
        sa.Column("votes", sa.Integer, server_default="0"),
        sa.Column("vote_percentage", sa.Float, nullable=True),
        sa.Column("result_status", sa.String(100), nullable=False),
        sa.Column("result_status_original", sa.String(255), nullable=True),
        sa.Column("elected", sa.Boolean, server_default="false"),
        sa.Column("elected_by_average", sa.Boolean, server_default="false"),
        sa.Column("substitute", sa.Boolean, server_default="false"),
        sa.Column("ranking", sa.Integer, nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Government plans
    op.create_table(
        "government_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("document_url", sa.String(2048), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("file_hash", sa.String(128), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("published_at", sa.Date, nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Campaign accountability
    op.create_table(
        "campaign_accountability",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidacy_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("candidacies.id"), index=True, nullable=False),
        sa.Column("status", sa.String(100), nullable=False),
        sa.Column("judgment_status", sa.String(100), nullable=True),
        sa.Column("submitted_at", sa.Date, nullable=True),
        sa.Column("judged_at", sa.Date, nullable=True),
        sa.Column("decision", sa.Text, nullable=True),
        sa.Column("decision_url", sa.String(2048), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # External datasets tracking
    op.create_table(
        "external_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_name", sa.String(100), index=True),
        sa.Column("dataset_name", sa.String(255), nullable=False),
        sa.Column("dataset_year", sa.Integer, nullable=True, index=True),
        sa.Column("dataset_url", sa.String(2048), nullable=True),
        sa.Column("resource_name", sa.String(255), nullable=True),
        sa.Column("resource_url", sa.String(2048), nullable=True),
        sa.Column("format", sa.String(20), nullable=True),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("last_modified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("status", sa.String(50), server_default="discovered"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("external_datasets")
    op.drop_table("campaign_accountability")
    op.drop_table("government_plans")
    op.drop_table("election_results")
    op.drop_table("campaign_expenses")
    op.drop_table("campaign_revenues")
    op.drop_table("candidate_assets")
    op.drop_index("ix_candidacies_tse_election", "candidacies")
    op.drop_table("candidacies")
    op.drop_table("elections")
