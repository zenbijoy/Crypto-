"""
CryptoScope AI - User, Watchlist, Alerts & Telegram Integration Service
Manages user authentication, profile data, personal watchlist items,
custom market/liquidation alerts, provider health states, and Telegram bot commands.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    tier: str  # PRO, INSTITUTIONAL, FREE
    api_key: str
    referral_code: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WatchlistItem(BaseModel):
    symbol: str
    asset: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None


class UserAlert(BaseModel):
    id: str
    symbol: str
    alert_type: str  # PRICE_ABOVE, PRICE_BELOW, LIQUIDATION_SPIKE, FUNDING_EXTREME, RADAR_TRIGGER
    threshold: float
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_triggered: Optional[datetime] = None


class ProviderStatusItem(BaseModel):
    provider_name: str
    category: str  # EXCHANGE, ONCHAIN, MACRO, SENTIMENT
    status: str  # HEALTHY, DEGRADED, OFFLINE
    latency_ms: float
    error_rate_pct: float
    rate_limit_remaining_pct: float
    last_ping: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TelegramCommandRequest(BaseModel):
    chat_id: int
    command: str
    args: Optional[str] = ""


class TelegramCommandResponse(BaseModel):
    chat_id: int
    command: str
    response_text: str
    parse_mode: str = "Markdown"


class UserWatchlistAlertsService:
    def __init__(self):
        self._users: Dict[str, UserProfile] = {
            "demo_user": UserProfile(
                id="usr_demo123",
                username="quant_trader",
                email="trader@cryptoscope.ai",
                tier="INSTITUTIONAL",
                api_key="cs_live_9f830a1b2c4e5d6f",
                referral_code="QUANT99"
            )
        }
        self._watchlist: List[WatchlistItem] = [
            WatchlistItem(symbol="BTCUSDT", asset="BTC", notes="Core long-term holding"),
            WatchlistItem(symbol="ETHUSDT", asset="ETH", notes="Ecosystem momentum"),
            WatchlistItem(symbol="SOLUSDT", asset="SOL", notes="High beta breakout")
        ]
        self._alerts: List[UserAlert] = [
            UserAlert(id="alt_1", symbol="BTCUSDT", alert_type="LIQUIDATION_SPIKE", threshold=5000000.0, is_active=True),
            UserAlert(id="alt_2", symbol="BTCUSDT", alert_type="PRICE_BELOW", threshold=77000.0, is_active=True),
            UserAlert(id="alt_3", symbol="SOLUSDT", alert_type="FUNDING_EXTREME", threshold=0.0300, is_active=True)
        ]

    def register(self, username: str, email: str) -> Dict[str, Any]:
        uid = f"usr_{uuid.uuid4().hex[:8]}"
        user = UserProfile(
            id=uid,
            username=username,
            email=email,
            tier="PRO",
            api_key=f"cs_live_{uuid.uuid4().hex[:16]}",
            referral_code=username.upper()[:6]
        )
        self._users[username] = user
        return {"token": f"jwt_{uuid.uuid4().hex}", "user": user}

    def login(self, username: str) -> Dict[str, Any]:
        user = self._users.get(username) or self._users["demo_user"]
        return {"token": f"jwt_{uuid.uuid4().hex}", "user": user}

    def get_user(self) -> UserProfile:
        return self._users["demo_user"]

    def get_watchlist(self) -> List[WatchlistItem]:
        return self._watchlist

    def add_watchlist(self, symbol: str) -> WatchlistItem:
        item = WatchlistItem(symbol=symbol.upper(), asset=symbol.upper().replace("USDT", ""))
        self._watchlist.append(item)
        return item

    def remove_watchlist(self, symbol: str) -> bool:
        self._watchlist = [w for w in self._watchlist if w.symbol != symbol.upper()]
        return True

    def get_alerts(self) -> List[UserAlert]:
        return self._alerts

    def create_alert(self, symbol: str, alert_type: str, threshold: float) -> UserAlert:
        alert = UserAlert(
            id=f"alt_{uuid.uuid4().hex[:6]}",
            symbol=symbol.upper(),
            alert_type=alert_type,
            threshold=threshold,
            is_active=True
        )
        self._alerts.append(alert)
        return alert

    def update_alert(self, alert_id: str, is_active: bool) -> Optional[UserAlert]:
        for a in self._alerts:
            if a.id == alert_id:
                a.is_active = is_active
                return a
        return None

    def delete_alert(self, alert_id: str) -> bool:
        self._alerts = [a for a in self._alerts if a.id != alert_id]
        return True

    def get_providers_status(self) -> List[ProviderStatusItem]:
        now = datetime.now(timezone.utc)
        return [
            ProviderStatusItem(provider_name="Binance Futures", category="EXCHANGE", status="HEALTHY", latency_ms=18.4, error_rate_pct=0.01, rate_limit_remaining_pct=92.5, last_ping=now),
            ProviderStatusItem(provider_name="Bybit Linear", category="EXCHANGE", status="HEALTHY", latency_ms=24.2, error_rate_pct=0.02, rate_limit_remaining_pct=88.0, last_ping=now),
            ProviderStatusItem(provider_name="OKX Swap", category="EXCHANGE", status="HEALTHY", latency_ms=31.5, error_rate_pct=0.01, rate_limit_remaining_pct=94.2, last_ping=now),
            ProviderStatusItem(provider_name="Alternative.me F&G", category="SENTIMENT", status="HEALTHY", latency_ms=85.0, error_rate_pct=0.0, rate_limit_remaining_pct=99.0, last_ping=now),
            ProviderStatusItem(provider_name="US Treasury Macro", category="MACRO", status="HEALTHY", latency_ms=42.0, error_rate_pct=0.0, rate_limit_remaining_pct=100.0, last_ping=now),
            ProviderStatusItem(provider_name="Bitcoin Mempool Node", category="ONCHAIN", status="HEALTHY", latency_ms=15.2, error_rate_pct=0.0, rate_limit_remaining_pct=98.5, last_ping=now)
        ]

    def handle_telegram_command(self, cmd: str, args: str, chat_id: int) -> TelegramCommandResponse:
        c = cmd.lower().replace("/", "").strip()
        if c == "market":
            txt = "*CryptoScope Market Overview*\n\n• BTC Price: $78,120 (+3.42%)\n• Total Futures OI: $106.9B\n• 24h Vol: $141.3B\n• L/S Ratio: 1.23 (Longs 48.67% / Shorts 51.33%)\n• 24h Liquidations: L $120.5M | S $71.5M\n• Fear & Greed: 70 (Greed)\n• BTC Dominance: 59.73%"
        elif c == "predict":
            sym = args.strip() or "BTC"
            txt = f"*AI Quant Prediction for {sym.upper()}*\n\n• Horizon: 15m\n• Direction: UP (Prob: 58%)\n• Expected Return: +0.45%\n• P50 Forecast: $78,471\n• 80% Range: [$77,550 - $78,690]\n• Uncertainty: 0.18 (Low)\n• Abstention: None (Active)"
        elif c == "funding":
            txt = "*Cross-Exchange Funding Rates*\n\n• BTC: +0.0100% (Annualized 10.95%)\n• ETH: +0.0085% (Annualized 9.30%)\n• SOL: +0.0125% (Annualized 13.70%)\n• Top Overheated: SUI (+0.0350%)\n• Top Negative: WIF (-0.0150%)"
        elif c == "radar":
            txt = "*Contract Radar Alert*\n\n⚠️ *BTCUSDT Risk Score: 82 (HIGH)*\n• Dominant Side: Longs at Risk\n• Primary Liquidation Pool: $77,200 ($84.2M concentration)\n• Distance: -1.18%\n• Recent 1h Liqs: 6 events"
        elif c == "feargreed":
            txt = "*Fear & Greed Index*\n\n• Current: 70 (Greed)\n• Yesterday: 61 (Greed)\n• 7 Days Ago: 73 (Greed)\n• 30 Days Ago: 28 (Fear)\n• Year High: 74 (2026-08-24)\n• Year Low: 5 (2026-02-07)"
        elif c == "liquidations":
            txt = "*24h Liquidation Summary*\n\n• Total: $192.12M\n• Longs: $120.59M (62.8%)\n• Shorts: $71.53M (37.2%)\n• Largest: $4.20M on BTCUSDT at $77,420\n• Imbalance: 1.69x Long Heavy"
        elif c == "orderflow":
            txt = "*Order Flow & CVD Telemetry*\n\n• BTC 1h Delta: +$14.2M\n• Taker Buy/Sell Ratio: 1.08\n• CVD Trend: Bullish Absorption\n• Book Imbalance: +0.12 (Bid Heavy)\n• Spread: 1.2 bps"
        else:
            txt = "*CryptoScope AI Bot Commands*\n\n/market - Real-time market overview\n/predict [symbol] - Multi-horizon AI prediction\n/funding - Funding rate matrix & heat\n/radar - Contract radar liquidation alerts\n/feargreed - Sentiment & historical stats\n/liquidations - Liquidation volume & largest trades\n/orderflow - CVD & taker trade telemetry\n/help - Command list"

        return TelegramCommandResponse(chat_id=chat_id, command=cmd, response_text=txt)


user_service = UserWatchlistAlertsService()
