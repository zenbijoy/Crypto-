"""
CryptoScope AI - DEPRECATED LEGACY BACKEND
DO NOT USE IN PRODUCTION.
The sole production backend is cryptoscope-ai/apps/api/main.py
"""
import sys

# Loud deprecation guard per Phase 10 specification
raise RuntimeError(
    "DEPRECATED: Use cryptoscope-ai/apps/api/main.py. "
    "The legacy prototype backend has been deprecated and archived."
)

from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import time
import json
import random

# App initialization with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    print("CryptoScope AI Backend initialized. Connecting streaming data feeds...")
    yield
    print("CryptoScope AI Backend shutting down.")

app = FastAPI(
    title="CryptoScope AI Intelligence API",
    description="Enterprise Crypto Futures Intelligence, Forecasting & Execution API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- SCHEMAS -----------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    sync_enabled: bool = True
    active_alerts_count: int = 2
    paper_positions_count: int = 2
    last_sync_utc: int

class MarketSummary(BaseModel):
    symbol: str
    asset: str
    pair: str
    last_price: float
    mark_price: float
    index_price: float
    change_24h_pct: float
    volume_24h_usd: float
    sparkline: List[float]
    market_type: str = "USDT_PERP"
    funding_rate: float
    open_interest: float
    volatility_24h: float

class Candle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class DirectionProbabilities(BaseModel):
    up: float
    sideways: float
    down: float

class PriceQuantiles(BaseModel):
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float

class FeatureAttribution(BaseModel):
    feature: str
    impact: float
    direction: str # "BULLISH" or "BEARISH"
    description: str

class Prediction(BaseModel):
    id: str
    asset: str
    symbol: str
    timestamp: int
    horizon: str
    current_price: float
    expected_return: float
    direction: str # "LONG", "SHORT", "NO_TRADE"
    signal: str    # "LONG", "STRONG_LONG", "SHORT", "STRONG_SHORT", "NO-TRADE"
    p_up: float
    p_down: float
    p_sideways: float
    price_p10: float
    price_p25: float
    price_p50: float
    price_p75: float
    price_p90: float
    expected_volatility: float
    confidence: int # 0-100
    model_agreement: int # 0-100
    regime: str
    data_quality: int # 0-100
    signal_reason: str
    risk_level: str # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    model_version: str
    generated_at: int
    stale_after: int
    attributions: List[FeatureAttribution] = []

class OrderBookLevel(BaseModel):
    price: float
    amount: float
    total: float

class OrderBookSnapshot(BaseModel):
    symbol: str
    timestamp: int
    sequence: int
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    spread: float
    relative_spread_bps: float
    mid_price: float
    microprice: float
    imbalance_pct: float
    book_pressure_bid_pct: float
    depth_10bps_usd: float

class LiquidationCluster(BaseModel):
    price_level: float
    volume_usd: float
    side: str # "LONG" or "SHORT"
    intensity: float

class LiquidationMetrics(BaseModel):
    symbol: str
    long_liq_1h_usd: float
    short_liq_1h_usd: float
    pressure_score: int # 0-100
    status_label: str
    clusters: List[LiquidationCluster]
    recent_events: List[Dict]

class SupportResistanceZone(BaseModel):
    type: str # "RESISTANCE" or "SUPPORT"
    min_price: float
    max_price: float
    strength: int # 0-100
    touches: int
    label: str

class StructureSummary(BaseModel):
    symbol: str
    trend: str
    structure_context: str
    zones: List[SupportResistanceZone]

class NewsCard(BaseModel):
    id: str
    title: str
    source: str
    time_ago: str
    category: str
    sentiment_tag: str # "GREEN", "GOLD", "RED"
    relevance_score: float

class SentimentSummary(BaseModel):
    symbol: str
    sentiment: str
    fear_and_greed_score: int
    fear_and_greed_label: str
    event_risk: str
    sentiment_history: List[float]
    news: List[NewsCard]

class OnChainSummary(BaseModel):
    asset: str
    exchange_netflow_btc: float
    whale_deposits: str
    sopr: float
    mvrv: float
    hash_rate: str
    active_addresses: str
    trend_history: List[float]
    interpretation: List[str]

class MacroEvent(BaseModel):
    name: str
    time_offset: str
    impact: str # "HIGH", "MED", "LOW"

class MacroSummary(BaseModel):
    next_event_title: str
    countdown: str
    fed_funds_rate: str
    us_10y_yield: str
    dxy_index: str
    sp500_daily: str
    gold_price: str
    vix_index: str
    events: List[MacroEvent]

class AlertRule(BaseModel):
    id: str
    asset: str
    horizon: str
    signal: str
    min_confidence: int
    min_model_agreement: int
    min_data_quality: int
    cooldown_minutes: int
    require_expected_edge: bool = True
    require_risk_engine_allow: bool = True
    status: str = "ACTIVE" # "ACTIVE", "TRIGGERED", "PAUSED"
    created_at: int
    last_checked_at: int
    triggers_count: int = 0

class PaperPosition(BaseModel):
    id: str
    symbol: str
    direction: str # "LONG" or "SHORT"
    entry_price: float
    mark_price: float
    size_usd: float
    leverage: int = 1
    unrealized_pnl: float
    unrealized_pnl_pct: float
    stop_loss: float
    take_profit: float
    entry_timestamp: int
    entry_ai_confidence: int
    entry_ai_regime: str
    entry_ai_model: str
    entry_ai_risk: str

class PaperOrderRequest(BaseModel):
    symbol: str
    direction: str
    order_type: str # "MARKET" or "LIMIT"
    size_usd: float
    stop_loss_pct: float
    take_profit_pct: float
    max_slippage_pct: float = 0.08

class SystemHealth(BaseModel):
    status: str
    quality_score: int
    market_data_latency_ms: int
    order_book_sync: str
    prediction_api_latency_ms: int
    redis_cache: str
    news_pipeline_lag: str
    onchain_provider: str
    circuit_breakers: Dict[str, str]

# ----------------- IN-MEMORY STATE -----------------
alerts_db: List[AlertRule] = [
    AlertRule(
        id="alert-1",
        asset="BTC",
        horizon="1 hour",
        signal="LONG",
        min_confidence=80,
        min_model_agreement=75,
        min_data_quality=95,
        cooldown_minutes=60,
        status="ACTIVE",
        created_at=int(time.time()) - 86400,
        last_checked_at=int(time.time()) - 120,
        triggers_count=3
    ),
    AlertRule(
        id="alert-2",
        asset="SOL",
        horizon="15 minutes",
        signal="BREAKOUT",
        min_confidence=75,
        min_model_agreement=70,
        min_data_quality=90,
        cooldown_minutes=30,
        status="ACTIVE",
        created_at=int(time.time()) - 43200,
        last_checked_at=int(time.time()) - 300,
        triggers_count=1
    ),
    AlertRule(
        id="alert-3",
        asset="ETH",
        horizon="1 hour",
        signal="OI SPIKE",
        min_confidence=85,
        min_model_agreement=80,
        min_data_quality=95,
        cooldown_minutes=60,
        status="PAUSED",
        created_at=int(time.time()) - 172800,
        last_checked_at=int(time.time()) - 3600,
        triggers_count=0
    )
]

paper_positions_db: List[PaperPosition] = [
    PaperPosition(
        id="pos-btc-1",
        symbol="BTC/USDT",
        direction="LONG",
        entry_price=107880.0,
        mark_price=109420.30,
        size_usd=2000.0,
        leverage=1,
        unrealized_pnl=144.20,
        unrealized_pnl_pct=7.21,
        stop_loss=106262.0,
        take_profit=111116.0,
        entry_timestamp=int(time.time()) - 14400,
        entry_ai_confidence=82,
        entry_ai_regime="Bull trend",
        entry_ai_model="btc-1h-v24.9",
        entry_ai_risk="MEDIUM"
    ),
    PaperPosition(
        id="pos-sol-1",
        symbol="SOL/USDT",
        direction="LONG",
        entry_price=201.20,
        mark_price=208.14,
        size_usd=1200.0,
        leverage=1,
        unrealized_pnl=53.00,
        unrealized_pnl_pct=4.42,
        stop_loss=196.50,
        take_profit=224.00,
        entry_timestamp=int(time.time()) - 7200,
        entry_ai_confidence=77,
        entry_ai_regime="Bull trend",
        entry_ai_model="sol-1h-v18.4",
        entry_ai_risk="MEDIUM"
    )
]

# ----------------- ENDPOINTS -----------------

@app.post("/v1/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    return TokenResponse(
        access_token="cryptoscope_jwt_token_secure_" + str(int(time.time())),
        user_name="Joy Saha",
        email=req.email if req.email else "you@example.com"
    )

@app.get("/v1/auth/profile", response_model=UserProfile)
async def get_profile():
    return UserProfile(
        id="usr-1002",
        email="you@example.com",
        name="Joy Saha",
        sync_enabled=True,
        active_alerts_count=len([a for a in alerts_db if a.status == "ACTIVE"]),
        paper_positions_count=len(paper_positions_db),
        last_sync_utc=int(time.time()) - 12
    )

@app.get("/v1/markets", response_model=List[MarketSummary])
async def get_markets():
    return [
        MarketSummary(
            symbol="BTCUSDT",
            asset="BTC",
            pair="BTC/USDT",
            last_price=109420.30,
            mark_price=109417.0,
            index_price=109419.5,
            change_24h_pct=2.43,
            volume_24h_usd=28400000000.0,
            sparkline=[107000.0, 107400.0, 106900.0, 108100.0, 108900.0, 109200.0, 109420.30],
            funding_rate=0.000091,
            open_interest=21400000000.0,
            volatility_24h=0.024
        ),
        MarketSummary(
            symbol="ETHUSDT",
            asset="ETH",
            pair="ETH/USDT",
            last_price=4386.50,
            mark_price=4385.90,
            index_price=4386.10,
            change_24h_pct=3.91,
            volume_24h_usd=14200000000.0,
            sparkline=[4210.0, 4240.0, 4220.0, 4310.0, 4350.0, 4370.0, 4386.50],
            funding_rate=0.000087,
            open_interest=11200000000.0,
            volatility_24h=0.031
        ),
        MarketSummary(
            symbol="SOLUSDT",
            asset="SOL",
            pair="SOL/USDT",
            last_price=208.14,
            mark_price=208.10,
            index_price=208.12,
            change_24h_pct=4.08,
            volume_24h_usd=6800000000.0,
            sparkline=[198.0, 199.5, 201.0, 200.2, 204.0, 206.8, 208.14],
            funding_rate=0.000079,
            open_interest=4900000000.0,
            volatility_24h=0.045
        ),
        MarketSummary(
            symbol="BNBUSDT",
            asset="BNB",
            pair="BNB/USDT",
            last_price=812.50,
            mark_price=812.30,
            index_price=812.40,
            change_24h_pct=-0.44,
            volume_24h_usd=1900000000.0,
            sparkline=[820.0, 818.0, 819.0, 815.0, 814.0, 812.50],
            funding_rate=0.000050,
            open_interest=1200000000.0,
            volatility_24h=0.018
        ),
        MarketSummary(
            symbol="XRPUSDT",
            asset="XRP",
            pair="XRP/USDT",
            last_price=3.02,
            mark_price=3.021,
            index_price=3.020,
            change_24h_pct=1.12,
            volume_24h_usd=3100000000.0,
            sparkline=[2.95, 2.97, 2.99, 3.01, 3.02],
            funding_rate=0.000062,
            open_interest=1800000000.0,
            volatility_24h=0.029
        ),
        MarketSummary(
            symbol="DOGEUSDT",
            asset="DOGE",
            pair="DOGE/USDT",
            last_price=0.237,
            mark_price=0.2369,
            index_price=0.2370,
            change_24h_pct=-1.08,
            volume_24h_usd=1500000000.0,
            sparkline=[0.242, 0.240, 0.239, 0.238, 0.237],
            funding_rate=0.000040,
            open_interest=850000000.0,
            volatility_24h=0.038
        )
    ]

@app.get("/v1/markets/{symbol}", response_model=MarketSummary)
async def get_market(symbol: str):
    markets = await get_markets()
    for m in markets:
        if m.symbol.upper() == symbol.upper() or m.asset.upper() == symbol.upper():
            return m
    return markets[0]

@app.get("/v1/candles/{symbol}", response_model=List[Candle])
async def get_candles(symbol: str, timeframe: str = "1h", limit: int = 30):
    base_price = 109400.0 if "BTC" in symbol.upper() else (4380.0 if "ETH" in symbol.upper() else 208.0)
    now = int(time.time())
    step = 3600 if timeframe == "1h" else (900 if timeframe == "15m" else 86400)
    candles = []
    p = base_price * 0.96
    for i in range(limit):
        t = now - (limit - i) * step
        o = p
        delta = random.uniform(-0.015, 0.02) * o
        c = o + delta
        h = max(o, c) + random.uniform(0.001, 0.008) * o
        l = min(o, c) - random.uniform(0.001, 0.008) * o
        v = random.uniform(500, 3500)
        p = c
        candles.append(Candle(timestamp=t, open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=round(v, 2)))
    return candles

@app.get("/v1/predictions/{symbol}", response_model=Prediction)
async def get_prediction(symbol: str, horizon: str = Query("1h")):
    sym = symbol.upper()
    is_btc = "BTC" in sym
    is_eth = "ETH" in sym
    is_sol = "SOL" in sym

    price = 109420.30 if is_btc else (4386.50 if is_eth else 208.14)
    conf = 82 if is_btc else (61 if is_eth else 77)
    sig = "LONG" if is_btc else ("NO-TRADE" if is_eth else "LONG")
    p_up = 0.68 if is_btc else (0.42 if is_eth else 0.64)
    p_side = 0.19 if is_btc else (0.38 if is_eth else 0.22)
    p_down = 0.13 if is_btc else (0.20 if is_eth else 0.14)
    exp_ret = 0.74 if is_btc else (0.05 if is_eth else 1.15)
    model_ver = f"{'btc' if is_btc else ('eth' if is_eth else 'sol')}-{horizon}-v24.9"

    return Prediction(
        id=f"pred-{sym.lower()}-{int(time.time())}",
        asset="BTC" if is_btc else ("ETH" if is_eth else "SOL"),
        symbol=f"{'BTC' if is_btc else ('ETH' if is_eth else 'SOL')}/USDT",
        timestamp=int(time.time()),
        horizon=horizon,
        current_price=price,
        expected_return=exp_ret,
        direction="LONG" if sig == "LONG" else "NEUTRAL",
        signal=sig,
        p_up=p_up,
        p_down=p_down,
        p_sideways=p_side,
        price_p10=round(price * 0.985, 2),
        price_p25=round(price * 0.993, 2),
        price_p50=round(price * 1.007, 2),
        price_p75=round(price * 1.018, 2),
        price_p90=round(price * 1.026, 2),
        expected_volatility=0.014,
        confidence=conf,
        model_agreement=84 if is_btc else 58,
        regime="Moderate Bullish" if is_btc else ("High Volatility Neutral" if is_eth else "Breakout Bullish"),
        data_quality=98,
        signal_reason="Spot CVD rising & positive order book imbalance with stable funding" if is_btc else "Model agreement below 75% threshold, risk engine enforces abstention",
        risk_level="MEDIUM" if is_btc else ("HIGH" if is_eth else "MEDIUM"),
        model_version=model_ver,
        generated_at=int(time.time()) - 30,
        stale_after=int(time.time()) + 300,
        attributions=[
            FeatureAttribution(feature="Spot CVD rising", impact=0.18, direction="BULLISH", description="Aggressive spot buying exceeding futures volume"),
            FeatureAttribution(feature="Order book imbalance positive", impact=0.14, direction="BULLISH", description="Bid depth higher than ask depth within 25bps"),
            FeatureAttribution(feature="OI expansion with price", impact=0.09, direction="BULLISH", description="New long expansion detected in perp markets"),
            FeatureAttribution(feature="Funding elevated", impact=-0.07, direction="BEARISH", description="Funding rate slightly above 7-day median baseline")
        ]
    )

@app.get("/v1/orderbook/{symbol}", response_model=OrderBookSnapshot)
async def get_orderbook(symbol: str):
    base_price = 109420.30 if "BTC" in symbol.upper() else 4386.50
    bids = []
    asks = []
    tot_bid = 0.0
    tot_ask = 0.0
    for i in range(5):
        p_bid = base_price - (i + 1) * 4.5
        amt_bid = round(0.72 + i * 0.35, 3)
        tot_bid += amt_bid
        bids.append(OrderBookLevel(price=round(p_bid, 1), amount=amt_bid, total=round(tot_bid, 3)))

        p_ask = base_price + (i + 1) * 4.5
        amt_ask = round(0.85 + i * 0.32, 3)
        tot_ask += amt_ask
        asks.append(OrderBookLevel(price=round(p_ask, 1), amount=amt_ask, total=round(tot_ask, 3)))

    return OrderBookSnapshot(
        symbol=symbol.upper(),
        timestamp=int(time.time()),
        sequence=18849204,
        bids=bids,
        asks=asks,
        spread=0.004,
        relative_spread_bps=0.4,
        mid_price=base_price,
        microprice=base_price + 0.70,
        imbalance_pct=21.0,
        book_pressure_bid_pct=61.0,
        depth_10bps_usd=8700000.0
    )

@app.get("/v1/derivatives/{symbol}", response_model=Dict)
async def get_derivatives(symbol: str):
    return {
        "symbol": symbol.upper(),
        "funding_current": "0.0091%",
        "funding_7d_zscore": "+1.42",
        "positioning_oi": "$21.4B",
        "positioning_oi_change_24h": "+1.9%",
        "top_trader_ls_ratio": 1.27,
        "top_trader_sentiment": "Long-heavy",
        "basis_annualized": "8.4%",
        "basis_change": "-0.7%",
        "exchanges": [
            {"name": "Binance", "funding": "0.0091%", "delta": "+0.0012%"},
            {"name": "Bybit", "funding": "0.0087%", "delta": "-0.0009%"},
            {"name": "OKX", "funding": "0.0079%", "delta": "+0.0051%"}
        ],
        "funding_history": [0.007, 0.008, 0.0085, 0.009, 0.0088, 0.0091]
    }

@app.get("/v1/liquidations/{symbol}", response_model=LiquidationMetrics)
async def get_liquidations(symbol: str):
    return LiquidationMetrics(
        symbol=symbol.upper(),
        long_liq_1h_usd=18400000.0,
        short_liq_1h_usd=9700000.0,
        pressure_score=64,
        status_label="ELEVATED",
        clusters=[
            LiquidationCluster(price_level=111200.0, volume_usd=45000000.0, side="SHORT", intensity=0.9),
            LiquidationCluster(price_level=110400.0, volume_usd=38000000.0, side="SHORT", intensity=0.75),
            LiquidationCluster(price_level=108200.0, volume_usd=52000000.0, side="LONG", intensity=0.95),
            LiquidationCluster(price_level=107100.0, volume_usd=29000000.0, side="LONG", intensity=0.6)
        ],
        recent_events=[
            {"side": "LONG", "price": 109118.0, "amount": "$630K", "time_ago": "2m"},
            {"side": "SHORT", "price": 109470.0, "amount": "$410K", "time_ago": "4m"},
            {"side": "LONG", "price": 108990.0, "amount": "$155K", "time_ago": "9m"},
            {"side": "LONG", "price": 108822.0, "amount": "$271K", "time_ago": "14m"}
        ]
    )

@app.get("/v1/levels/{symbol}", response_model=StructureSummary)
async def get_levels(symbol: str):
    return StructureSummary(
        symbol=symbol.upper(),
        trend="Higher High / Higher Low",
        structure_context="Bull trend expansion with consolidation above 108.5K",
        zones=[
            SupportResistanceZone(type="RESISTANCE", min_price=110800.0, max_price=111300.0, strength=88, touches=4, label="Major Sell Wall"),
            SupportResistanceZone(type="RESISTANCE", min_price=113400.0, max_price=114000.0, strength=71, touches=2, label="Liquidity Sweep Target"),
            SupportResistanceZone(type="SUPPORT", min_price=107600.0, max_price=108100.0, strength=91, touches=6, label="Primary Buyer Defense Zone"),
            SupportResistanceZone(type="SUPPORT", min_price=105900.0, max_price=106500.0, strength=78, touches=3, label="Secondary Structural Level")
        ]
    )

@app.get("/v1/sentiment/{symbol}", response_model=SentimentSummary)
async def get_sentiment(symbol: str):
    return SentimentSummary(
        symbol=symbol.upper(),
        sentiment="BULLISH",
        fear_and_greed_score=74,
        fear_and_greed_label="Greed",
        event_risk="LOW",
        sentiment_history=[65.0, 68.0, 71.0, 70.0, 74.0],
        news=[
            NewsCard(id="n1", title="ETF flows strengthen with institutional net inflows +$420M", source="Bloomberg Crypto", time_ago="2m", category="ETF", sentiment_tag="GREEN", relevance_score=0.95),
            NewsCard(id="n2", title="Exchange scheduled maintenance window completed with zero latency impact", source="Official Announcement", time_ago="23m", category="Ops", sentiment_tag="GOLD", relevance_score=0.72),
            NewsCard(id="n3", title="Macro bond yields ease after cooling inflation indicators", source="Reuters Financial", time_ago="45m", category="Macro", sentiment_tag="GREEN", relevance_score=0.88),
            NewsCard(id="n4", title="Regulatory hearing scheduled for next quarter draft framework", source="CoinDesk News", time_ago="2h", category="Regulation", sentiment_tag="RED", relevance_score=0.65)
        ]
    )

@app.get("/v1/onchain/{asset}", response_model=OnChainSummary)
async def get_onchain(asset: str):
    return OnChainSummary(
        asset=asset.upper(),
        exchange_netflow_btc=-12800.0,
        whale_deposits="Low (22% below 30d avg)",
        sopr=1.04,
        mvrv=2.18,
        hash_rate="812 EH/s",
        active_addresses="894K (+3.2%)",
        trend_history=[1.01, 1.02, 1.03, 1.02, 1.04],
        interpretation=[
            "Exchange reserves declining steadily (-12.8K BTC 24h)",
            "Whale exchange deposits remain below 30-day baseline",
            "SOPR > 1 indicates healthy profit realization without panic selling"
        ]
    )

@app.get("/v1/macro", response_model=MacroSummary)
async def get_macro():
    return MacroSummary(
        next_event_title="US CPI Release",
        countdown="18H 22M",
        fed_funds_rate="5.25%",
        us_10y_yield="4.12%",
        dxy_index="101.8",
        sp500_daily="+0.82%",
        gold_price="$2,484",
        vix_index="15.9",
        events=[
            MacroEvent(name="US CPI Release", time_offset="18h", impact="HIGH"),
            MacroEvent(name="FOMC Minutes", time_offset="2d", impact="HIGH"),
            MacroEvent(name="Quarterly ETF options expiry", time_offset="4d", impact="MED"),
            MacroEvent(name="US NFP Report", time_offset="6d", impact="HIGH")
        ]
    )

@app.get("/v1/alerts", response_model=List[AlertRule])
async def get_alerts():
    return alerts_db

@app.post("/v1/alerts", response_model=AlertRule)
async def create_alert(alert: AlertRule):
    alerts_db.append(alert)
    return alert

@app.delete("/v1/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    global alerts_db
    alerts_db = [a for a in alerts_db if a.id != alert_id]
    return {"status": "DELETED", "id": alert_id}

@app.get("/v1/paper/positions", response_model=List[PaperPosition])
async def get_paper_positions():
    return paper_positions_db

@app.post("/v1/paper/order", response_model=PaperPosition)
async def place_paper_order(order: PaperOrderRequest):
    price = 109420.30 if "BTC" in order.symbol.upper() else 208.14
    new_pos = PaperPosition(
        id=f"pos-{int(time.time())}",
        symbol=order.symbol,
        direction=order.direction,
        entry_price=price,
        mark_price=price,
        size_usd=order.size_usd,
        leverage=1,
        unrealized_pnl=0.0,
        unrealized_pnl_pct=0.0,
        stop_loss=round(price * (1 - order.stop_loss_pct/100.0) if order.direction == "LONG" else price * (1 + order.stop_loss_pct/100.0), 2),
        take_profit=round(price * (1 + order.take_profit_pct/100.0) if order.direction == "LONG" else price * (1 - order.take_profit_pct/100.0), 2),
        entry_timestamp=int(time.time()),
        entry_ai_confidence=82,
        entry_ai_regime="Bull trend",
        entry_ai_model="btc-1h-v24.9",
        entry_ai_risk="MEDIUM"
    )
    paper_positions_db.append(new_pos)
    return new_pos

@app.post("/v1/paper/positions/{pos_id}/close")
async def close_paper_position(pos_id: str):
    global paper_positions_db
    paper_positions_db = [p for p in paper_positions_db if p.id != pos_id]
    return {"status": "CLOSED", "id": pos_id}

@app.get("/v1/performance")
async def get_performance():
    return {
        "signals_count": 184,
        "coverage_pct": 21.0,
        "precision_pct": 71.2,
        "brier_score": 0.164,
        "paper_net_result_pct": 6.8,
        "paper_max_drawdown_pct": -4.8,
        "paper_profit_factor": 1.42,
        "rolling_precision": [68.0, 70.0, 72.0, 71.0, 73.0, 71.2],
        "by_horizon": [
            {"horizon": "5m", "precision": "67% precision", "coverage": "32% coverage"},
            {"horizon": "15m", "precision": "72% precision", "coverage": "24% coverage"},
            {"horizon": "1h", "precision": "75% precision", "coverage": "18% coverage"},
            {"horizon": "4h", "precision": "69% precision", "coverage": "11% coverage"}
        ]
    }

@app.get("/v1/models")
async def get_models():
    return {
        "champion": {
            "name": "btc-1h-v24.9",
            "stage": "PRODUCTION",
            "balanced_acc": "68.4%",
            "brier": "0.158",
            "coverage": "18%"
        },
        "challengers": [
            {"name": "btc-1h-v25.1", "stage": "SHADOW", "brier": "0.155"},
            {"name": "btc-1h-v25.0", "stage": "CANDIDATE", "brier": "0.161"},
            {"name": "btc-1h-v24.8", "stage": "PAPER", "precision": "70.8%"}
        ],
        "drift_status": {
            "feature_drift": "NORMAL",
            "prediction_drift": "NORMAL",
            "psi_score": 0.04
        }
    }

@app.get("/v1/system/health", response_model=SystemHealth)
async def get_system_health():
    return SystemHealth(
        status="Operational",
        quality_score=98,
        market_data_latency_ms=12,
        order_book_sync="Synced (seq #18849204)",
        prediction_api_latency_ms=38,
        redis_cache="Healthy (0.4ms)",
        news_pipeline_lag="2m lag",
        onchain_provider="Healthy",
        circuit_breakers={
            "Data feed stale": "CLEAR",
            "WebSocket gap": "CLEAR",
            "Extreme spread": "CLEAR",
            "Model mismatch": "CLEAR"
        }
    )

# WebSocket streaming endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Broadcast simulated real-time ticks
            tick = {
                "type": "TICK",
                "timestamp": int(time.time()),
                "btc_price": round(109420.30 + random.uniform(-15.0, 15.0), 2),
                "eth_price": round(4386.50 + random.uniform(-1.5, 1.5), 2),
                "sol_price": round(208.14 + random.uniform(-0.4, 0.4), 2),
                "order_book_imbalance": round(21.0 + random.uniform(-3.0, 3.0), 1),
                "funding_rate": 0.000091
            }
            await websocket.send_text(json.dumps(tick))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
