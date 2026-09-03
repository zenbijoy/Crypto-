"""initial_truthful_schema

Revision ID: 001_initial_truthful_schema
Revises: 
Create Date: 2026-09-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_truthful_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Schema creation managed dynamically via models Base.metadata.create_all
    pass

def downgrade() -> None:
    pass
