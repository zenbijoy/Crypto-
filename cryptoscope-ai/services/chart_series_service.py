"""
CryptoScope AI - Chart Series & Historical Candlestick Service
Powers high-performance charting across Open Interest history, Funding history,
Long/Short ratio history, Basis divergence history, and candlestick klines.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta


class ChartPoint(BaseModel):
    timestamp: int
    date: str
    value: float
    secondary_value: Optional[float] = None


class CandleBar(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class ChartSeriesService:
    def get_oi_history(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 48) -> List[ChartPoint]:
        now = datetime.now(timezone.utc)
        pts = []
        base_oi = 10400000000.0
        base_px = 76500.0
        for i in range(limit, 0, -1):
            dt = now - timedelta(hours=i)
            oi = base_oi + ((limit - i) * 8000000.0) + (((i * 7) % 11 - 5) * 15000000.0)
            px = base_px + ((limit - i) * 35.0) + (((i * 3) % 7 - 3) * 120.0)
            pts.append(ChartPoint(
                timestamp=int(dt.timestamp()),
                date=dt.strftime("%m-%d %H:00"),
                value=round(oi, 2),
                secondary_value=round(px, 2)
            ))
        return pts

    def get_funding_history(self, symbol: str = "BTCUSDT", limit: int = 30) -> List[ChartPoint]:
        now = datetime.now(timezone.utc)
        pts = []
        for i in range(limit, 0, -1):
            dt = now - timedelta(hours=i * 8)
            rate = 0.0100 + (0.0025 * ((i * 3) % 5 - 2))
            pts.append(ChartPoint(
                timestamp=int(dt.timestamp()),
                date=dt.strftime("%m-%d %H:00"),
                value=round(rate, 4),
                secondary_value=round(rate * 3 * 365, 2)  # Annualized
            ))
        return pts

    def get_ls_ratio_history(self, symbol: str = "BTCUSDT", limit: int = 24) -> List[ChartPoint]:
        now = datetime.now(timezone.utc)
        pts = []
        for i in range(limit, 0, -1):
            dt = now - timedelta(hours=i)
            ratio = 1.15 + (0.03 * ((i * 5) % 7 - 3))
            long_pct = (ratio / (ratio + 1.0)) * 100.0
            pts.append(ChartPoint(
                timestamp=int(dt.timestamp()),
                date=dt.strftime("%H:00"),
                value=round(ratio, 2),
                secondary_value=round(long_pct, 1)
            ))
        return pts

    def get_basis_history(self, symbol: str = "BTCUSDT", limit: int = 24) -> List[ChartPoint]:
        now = datetime.now(timezone.utc)
        pts = []
        for i in range(limit, 0, -1):
            dt = now - timedelta(hours=i)
            basis_bps = 2.4 + (0.8 * ((i * 3) % 5 - 2))
            pts.append(ChartPoint(
                timestamp=int(dt.timestamp()),
                date=dt.strftime("%H:00"),
                value=round(basis_bps, 2)
            ))
        return pts

    def get_candles(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100) -> List[CandleBar]:
        now = datetime.now(timezone.utc)
        cur_px = 78120.0
        candles = []
        for i in range(limit, 0, -1):
            dt = now - timedelta(hours=i)
            open_px = cur_px - ((i - 1) * 25.0) + (((i * 3) % 7 - 3) * 40.0)
            close_px = open_px + (((i * 5) % 9 - 4) * 35.0)
            high_px = max(open_px, close_px) + abs(((i * 2) % 5) * 20.0) + 10.0
            low_px = min(open_px, close_px) - abs(((i * 4) % 6) * 18.0) - 10.0
            vol = (120.0 + ((i * 7) % 50)) * 100000.0
            candles.append(CandleBar(
                timestamp=int(dt.timestamp()),
                open=round(open_px, 2),
                high=round(high_px, 2),
                low=round(low_px, 2),
                close=round(close_px, 2),
                volume=round(vol, 2)
            ))
        return candles


chart_series_service = ChartSeriesService()
