"""Unify tag audit values and foreign key naming.

Revision ID: b4c8e03d7a21
Revises: a3b7d92c6f10
"""
from alembic import op
import sqlalchemy as sa


revision = "b4c8e03d7a21"
down_revision = "a3b7d92c6f10"
branch_labels = None
depends_on = None

_BASE_ENTITIES = (
    "CLIENT", "COMMAND", "DOMAIN", "ENVIRONMENT", "LINK", "NOTE",
    "PROJECT", "REPOSITORY", "SERVICE",
)


def _rename_audit_value(old: str, new: str) -> None:
    # Temporarily accept both values so MySQL can convert existing rows safely.
    op.alter_column(
        "logs", "affected_entity",
        existing_type=sa.Enum(*_BASE_ENTITIES, old, name="entity_type"),
        type_=sa.Enum(*_BASE_ENTITIES, old, new, name="entity_type"),
        existing_nullable=False,
    )
    op.execute(sa.text(
        "UPDATE logs SET affected_entity = :new, "
        "search_text = REPLACE(search_text, :old, :new) "
        "WHERE affected_entity = :old"
    ).bindparams(old=old, new=new))
    op.alter_column(
        "logs", "affected_entity",
        existing_type=sa.Enum(*_BASE_ENTITIES, old, new, name="entity_type"),
        type_=sa.Enum(*_BASE_ENTITIES, new, name="entity_type"),
        existing_nullable=False,
    )


def _rename_foreign_key(old: str, new: str) -> None:
    op.drop_constraint(old, "tags", type_="foreignkey")
    op.create_foreign_key(new, "tags", "clients", ["client_id"], ["id"], ondelete="CASCADE")


def upgrade() -> None:
    _rename_audit_value("CLIENT_TAG", "TAG")
    _rename_foreign_key("fk_client_tags_client_id_clients", "fk_tags_client_id_clients")


def downgrade() -> None:
    _rename_foreign_key("fk_tags_client_id_clients", "fk_client_tags_client_id_clients")
    _rename_audit_value("TAG", "CLIENT_TAG")
