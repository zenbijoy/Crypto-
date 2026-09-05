"""initial_truthful_schema

Revision ID: 001_initial_truthful_schema
Revises: 
Create Date: 2026-09-04

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_truthful_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Product schema - user_profiles
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(length=64), nullable=False, unique=True),
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
    )
    op.create_index('idx_user_profiles_uid', 'user_profiles', ['user_id'])

    # 2. Watchlists
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_watchlists_uid_sym', 'watchlists', ['user_id', 'symbol'])

    # 3. Quant - Instruments
    op.create_table(
        'instruments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(length=20), nullable=False, unique=True),
        sa.Column('base_asset', sa.String(length=10), nullable=False),
        sa.Column('quote_asset', sa.String(length=10), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('market_type', sa.String(length=20), server_default='PERPETUAL'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # 4. Quant - Candles
    op.create_table(
        'candles',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('resolution', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('quote_volume', sa.Float(), server_default='0.0'),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
    )
    op.create_index('idx_candles_sym_res_ts', 'candles', ['symbol', 'resolution', 'timestamp'])

    # 5. Quant - Trades
    op.create_table(
        'trades',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('trade_id', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
    )
    op.create_index('idx_trades_sym_ts', 'trades', ['symbol', 'timestamp'])

    # 6. Quant - Funding Rates
    op.create_table(
        'funding_rates',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('rate_7d_zscore', sa.Float(), nullable=True),
        sa.Column('mark_price', sa.Float(), nullable=True),
    )
    op.create_index('idx_funding_sym_ts', 'funding_rates', ['symbol', 'timestamp'])

    # 7. Quant - Open Interest
    op.create_table(
        'open_interest',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default='BINANCE'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open_interest_usd', sa.Float(), nullable=False),
        sa.Column('open_interest_contracts', sa.Float(), server_default='0.0'),
        sa.Column('oi_velocity', sa.Float(), server_default='0.0'),
    )
    op.create_index('idx_oi_sym_ts', 'open_interest', ['symbol', 'timestamp'])

    # 8. Quant - Predictions
    op.create_table(
        'predictions',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('horizon', sa.String(length=10), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_type', sa.String(length=50), server_default='EXPERIMENTAL_HEURISTIC'),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=False),
        sa.Column('expected_return_pct', sa.Float(), nullable=False),
        sa.Column('p10', sa.Float(), nullable=False),
        sa.Column('p25', sa.Float(), nullable=False),
        sa.Column('p50', sa.Float(), nullable=False),
        sa.Column('p75', sa.Float(), nullable=False),
        sa.Column('p90', sa.Float(), nullable=False),
        sa.Column('calibrated_confidence', sa.Integer(), server_default='0'),
        sa.Column('is_abstaining', sa.Boolean(), server_default='false'),
    )
    op.create_index('idx_pred_sym_hz_ts', 'predictions', ['symbol', 'horizon', 'timestamp'])

    # 9. Alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('horizon', sa.String(length=10), server_default='1h'),
        sa.Column('min_confidence', sa.Integer(), server_default='80'),
        sa.Column('signal_type', sa.String(length=20), server_default='LONG'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('predictions')
    op.drop_table('open_interest')
    op.drop_table('funding_rates')
    op.drop_table('trades')
    op.drop_table('candles')
    op.drop_table('instruments')
    op.drop_table('watchlists')
    op.drop_table('user_profiles')
