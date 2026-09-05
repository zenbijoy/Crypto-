"""foundation_schemas_and_timescale

Revision ID: 002_foundation_schemas
Revises: 001_initial_truthful_schema
Create Date: 2026-09-04

Implements Phase 6, Phase 7, Phase 8, Phase 9:
- Schemas: product, quant, mlops, audit
- TimescaleDB extension and hypertables for time-series quant tables
- user_profiles table keyed by Supabase UUID
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_foundation_schemas'
down_revision: Union[str, None] = '001_initial_truthful_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        # Create TimescaleDB extension if available
        op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

        # Create explicit schemas
        op.execute("CREATE SCHEMA IF NOT EXISTS product;")
        op.execute("CREATE SCHEMA IF NOT EXISTS quant;")
        op.execute("CREATE SCHEMA IF NOT EXISTS mlops;")
        op.execute("CREATE SCHEMA IF NOT EXISTS audit;")

    # -------------------------------------------------------------
    # PRODUCT SCHEMA
    # -------------------------------------------------------------
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('supabase_user_id', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('timezone', sa.String(length=50), server_default='UTC'),
        sa.Column('preferred_currency', sa.String(length=10), server_default='USD'),
        sa.Column('default_asset', sa.String(length=20), server_default='BTC'),
        sa.Column('default_horizon', sa.String(length=10), server_default='1h'),
        sa.Column('theme', sa.String(length=20), server_default='dark'),
        sa.Column('language', sa.String(length=10), server_default='en'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        schema='product' if is_postgres else None
    )
    op.create_index(
        'idx_user_profiles_uid',
        'user_profiles',
        ['user_id'],
        unique=True,
        schema='product' if is_postgres else None
    )

    # -------------------------------------------------------------
    # QUANT SCHEMA
    # -------------------------------------------------------------
    op.create_table(
        'instruments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('base_asset', sa.String(length=10), nullable=False),
        sa.Column('quote_asset', sa.String(length=10), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('market_type', sa.String(length=20), server_default='PERPETUAL'),
        sa.Column('contract_type', sa.String(length=20), server_default='LINEAR'),
        sa.Column('tick_size', sa.Float(), server_default='0.01'),
        sa.Column('step_size', sa.Float(), server_default='0.001'),
        sa.Column('min_quantity', sa.Float(), server_default='0.001'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        schema='quant' if is_postgres else None
    )

    # quant.candles
    op.create_table(
        'candles',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('resolution', sa.String(length=10), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('quote_volume', sa.Float(), server_default='0.0'),
        sa.Column('taker_buy_volume', sa.Float(), server_default='0.0'),
        sa.Column('trades_count', sa.Integer(), server_default='0'),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        schema='quant' if is_postgres else None
    )
    op.create_index(
        'idx_candles_sym_res_ts',
        'candles',
        ['symbol', 'resolution', 'timestamp'],
        schema='quant' if is_postgres else None
    )

    # quant.funding_rates
    op.create_table(
        'funding_rates',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('rate_7d_zscore', sa.Float(), nullable=True),
        sa.Column('mark_price', sa.Float(), nullable=True),
        schema='quant' if is_postgres else None
    )

    # quant.open_interest
    op.create_table(
        'open_interest',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('open_interest', sa.Float(), nullable=False),
        sa.Column('open_interest_usd', sa.Float(), nullable=False),
        schema='quant' if is_postgres else None
    )

    # quant.liquidations
    op.create_table(
        'liquidations',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('usd_value', sa.Float(), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        schema='quant' if is_postgres else None
    )

    # quant.orderbook_metrics
    op.create_table(
        'orderbook_metrics',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('bid_depth_usd', sa.Float(), nullable=False),
        sa.Column('ask_depth_usd', sa.Float(), nullable=False),
        sa.Column('imbalance_ratio', sa.Float(), nullable=False),
        sa.Column('spread_bps', sa.Float(), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        schema='quant' if is_postgres else None
    )

    # quant.feature_values
    op.create_table(
        'feature_values',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('horizon', sa.String(length=10), nullable=False),
        sa.Column('features', sa.JSON(), nullable=False),
        sa.Column('feature_version', sa.String(length=20), server_default='v1'),
        schema='quant' if is_postgres else None
    )

    # quant.predictions
    op.create_table(
        'predictions',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('horizon', sa.String(length=10), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('p10', sa.Float(), nullable=False),
        sa.Column('p50', sa.Float(), nullable=False),
        sa.Column('p90', sa.Float(), nullable=False),
        sa.Column('prob_up', sa.Float(), nullable=False),
        sa.Column('prob_down', sa.Float(), nullable=False),
        sa.Column('prob_sideways', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=False),
        sa.Column('shap_attributions', sa.JSON(), nullable=True),
        schema='quant' if is_postgres else None
    )

    # Convert time-series tables to TimescaleDB hypertables if in PostgreSQL
    if is_postgres:
        op.execute("SELECT create_hypertable('quant.candles', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.funding_rates', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.open_interest', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.liquidations', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.orderbook_metrics', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.feature_values', 'timestamp', if_not_exists => TRUE);")
        op.execute("SELECT create_hypertable('quant.predictions', 'timestamp', if_not_exists => TRUE);")


def downgrade() -> None:
    pass
