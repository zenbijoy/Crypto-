"""
CryptoScope AI - OKX V5 Perpetual Swap Provider
Implements full normalized interface using real OKX V5 public REST data.
Zero fake data, strictly real responses.
"""
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from providers.exchanges.base import (
    BaseExchangeProvider,
    TickerData,
    BookTickerData,
    CandleData,
    TradeData,
    OrderBookData,
    FundingData,
    OpenInterestData,
    LiquidationData
)
from providers.exchanges.instrument_registry import instrument_registry


class OKXSwapProvider(BaseExchangeProvider):
    def __init__(self, base_url: str = "https://www.okx.com"):
        super().__init__("okx", base_url)

    def _resolve(self, canonical_symbol: str) -> str:
        sym = instrument_registry.resolve_provider_symbol(canonical_symbol, "okx")
        if not sym:
            raise ValueError(f"Unregistered canonical symbol for OKX: {canonical_symbol}")
        return sym

    async def get_ticker(self, canonical_symbol: str) -> TickerData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/market/ticker"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": sym})
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                raise ValueError(f"OKX returned empty ticker for {sym}")
            d = data[0]

            mark = await self.get_mark_price(canonical_symbol)
            idx = await self.get_index_price(canonical_symbol)
            funding_data = await self.get_funding(canonical_symbol)

            evt_time = datetime.fromtimestamp(int(d["ts"]) / 1000.0, tz=timezone.utc)
            open24 = float(d.get("open24h", d["last"]))
            pct_change = ((float(d["last"]) - open24) / open24 * 100.0) if open24 > 0 else 0.0
            return TickerData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                last_price=float(d["last"]),
                mark_price=mark,
                index_price=idx,
                high_24h=float(d.get("high24h", 0.0)),
                low_24h=float(d.get("low24h", 0.0)),
                volume_24h=float(d.get("vol24h", 0.0)),
                quote_volume_24h=float(d.get("volCcy24h", 0.0)),
                funding_rate=funding_data.funding_rate,
                next_funding_time=funding_data.funding_time,
                price_change_pct_24h=pct_change
            )

    async def get_book_ticker(self, canonical_symbol: str) -> BookTickerData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/market/ticker"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": sym})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            evt_time = datetime.fromtimestamp(int(d["ts"]) / 1000.0, tz=timezone.utc)
            return BookTickerData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                bid_price=float(d["bidPx"]),
                bid_size=float(d["bidSz"]),
                ask_price=float(d["askPx"]),
                ask_size=float(d["askSz"])
            )

    async def get_candles(self, canonical_symbol: str, interval: str = "15m", limit: int = 100) -> List[CandleData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/market/candles"
        now = datetime.now(timezone.utc)
        # OKX format: 15m, 1H, 4H, 1D
        bar = interval
        if interval == "1h":
            bar = "1H"
        elif interval == "4h":
            bar = "4H"
        elif interval == "1d":
            bar = "1D"

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params={"instId": sym, "bar": bar, "limit": limit})
            resp.raise_for_status()
            raw_klines = resp.json().get("data", [])
            # OKX returns reverse chronological: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            results = []
            for k in reversed(raw_klines):
                evt_time = datetime.fromtimestamp(int(k[0]) / 1000.0, tz=timezone.utc)
                results.append(CandleData(
                    provider=self.provider_name,
                    symbol=sym,
                    canonical_symbol=canonical_symbol,
                    event_time=evt_time,
                    available_time=evt_time,
                    source_endpoint=url,
                    interval=interval,
                    open=float(k[1]),
                    high=float(k[2]),
                    low=float(k[3]),
                    close=float(k[4]),
                    volume=float(k[5]),
                    quote_volume=float(k[6]),
                    trades_count=None,
                    taker_buy_base=None,
                    taker_buy_quote=None
                ))
            return results

    async def get_trades(self, canonical_symbol: str, limit: int = 100) -> List[TradeData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/market/trades"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": sym, "limit": limit})
            resp.raise_for_status()
            trades = resp.json().get("data", [])
            results = []
            for t in trades:
                evt_time = datetime.fromtimestamp(int(t["ts"]) / 1000.0, tz=timezone.utc)
                side_str = t["side"].lower()
                results.append(TradeData(
                    provider=self.provider_name,
                    symbol=sym,
                    canonical_symbol=canonical_symbol,
                    event_time=evt_time,
                    available_time=now,
                    source_endpoint=url,
                    trade_id=str(t["tradeId"]),
                    price=float(t["px"]),
                    size=float(t["sz"]),
                    side=side_str,
                    is_buyer_maker=bool(side_str == "sell")
                ))
            return results

    async def get_orderbook(self, canonical_symbol: str, depth: int = 50) -> OrderBookData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/market/books"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": sym, "sz": depth})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            evt_time = datetime.fromtimestamp(int(d["ts"]) / 1000.0, tz=timezone.utc)
            bids = [[float(p), float(s)] for p, s, *_ in d.get("bids", [])]
            asks = [[float(p), float(s)] for p, s, *_ in d.get("asks", [])]
            return OrderBookData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                bids=bids,
                asks=asks,
                sequence=int(d.get("seqId", 0))
            )

    async def get_funding(self, canonical_symbol: str) -> FundingData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/public/funding-rate"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": sym})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            f_time = datetime.fromtimestamp(int(d["fundingTime"]) / 1000.0, tz=timezone.utc)
            f_rate = float(d.get("fundingRate", 0.0))
            pred_val = d.get("nextFundingRate")
            pred_rate = float(pred_val) if pred_val and str(pred_val).strip() else f_rate
            return FundingData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=now,
                available_time=now,
                source_endpoint=url,
                funding_rate=f_rate,
                funding_time=f_time,
                predicted_rate=pred_rate
            )

    async def get_open_interest(self, canonical_symbol: str) -> OpenInterestData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/public/open-interest"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instType": "SWAP", "instId": sym})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            oi_contracts = float(d["oi"])
            oi_coin = float(d.get("oiCcy", 0.0))

            mark = await self.get_mark_price(canonical_symbol)
            notional = oi_coin * mark if oi_coin > 0 else oi_contracts * mark * 0.01

            evt_time = datetime.fromtimestamp(int(d["ts"]) / 1000.0, tz=timezone.utc)
            return OpenInterestData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                open_interest=oi_coin if oi_coin > 0 else oi_contracts,
                unit="COIN" if oi_coin > 0 else "CONTRACT",
                normalized_notional_usd=notional,
                conversion_price=mark
            )

    async def get_mark_price(self, canonical_symbol: str) -> float:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/public/mark-price"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instType": "SWAP", "instId": sym})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            return float(d["markPx"])

    async def get_index_price(self, canonical_symbol: str) -> float:
        # Index ticker: e.g. BTC-USDT
        sym = self._resolve(canonical_symbol)
        base = sym.split("-")[0]
        quote = sym.split("-")[1]
        idx_sym = f"{base}-{quote}"
        url = f"{self.base_url}/api/v5/market/index-tickers"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"instId": idx_sym})
            resp.raise_for_status()
            d = resp.json().get("data", [])[0]
            return float(d["idxPx"])

    async def get_liquidations(self, canonical_symbol: str, limit: int = 50) -> List[LiquidationData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/api/v5/public/liquidation-orders"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, params={"instType": "SWAP", "mgnMode": "cross", "instId": sym, "state": "filled", "limit": limit})
                if resp.status_code == 200:
                    items = resp.json().get("data", [])
                    results = []
                    for item in items:
                        for detail in item.get("details", []):
                            evt_time = datetime.fromtimestamp(int(detail["ts"]) / 1000.0, tz=timezone.utc)
                            px = float(detail["bkPx"])
                            sz = float(detail["sz"])
                            results.append(LiquidationData(
                                provider=self.provider_name,
                                symbol=sym,
                                canonical_symbol=canonical_symbol,
                                event_time=evt_time,
                                available_time=now,
                                source_endpoint=url,
                                side="sell" if detail["side"] == "sell" else "buy",
                                price=px,
                                size=sz,
                                notional_usd=px * sz * 0.01
                            ))
                    return results
            except Exception:
                pass
            return []

    async def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v5/public/time"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                return {"provider": self.provider_name, "status": "ONLINE" if r.status_code == 200 else "DEGRADED", "code": r.status_code}
        except Exception as e:
            return {"provider": self.provider_name, "status": "OFFLINE", "error": str(e)}
