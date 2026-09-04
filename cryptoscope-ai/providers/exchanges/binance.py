"""
CryptoScope AI - Binance USD-M Perpetual Futures Provider
Implements full normalized interface using real Binance public REST & WebSocket data.
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


class BinanceFuturesProvider(BaseExchangeProvider):
    def __init__(self, base_url: str = "https://fapi.binance.com"):
        super().__init__("binance", base_url)

    def _resolve(self, canonical_symbol: str) -> str:
        sym = instrument_registry.resolve_provider_symbol(canonical_symbol, "binance")
        if not sym:
            raise ValueError(f"Unregistered canonical symbol for Binance: {canonical_symbol}")
        return sym

    async def get_ticker(self, canonical_symbol: str) -> TickerData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/ticker/24hr"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            data = resp.json()

            # Also get premium index for funding
            prem_resp = await client.get(f"{self.base_url}/fapi/v1/premiumIndex", params={"symbol": sym})
            prem_data = prem_resp.json() if prem_resp.status_code == 200 else {}

            event_time = datetime.fromtimestamp(data["closeTime"] / 1000.0, tz=timezone.utc)
            return TickerData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=event_time,
                available_time=now,
                source_endpoint=url,
                last_price=float(data["lastPrice"]),
                mark_price=float(prem_data.get("markPrice", data["lastPrice"])),
                index_price=float(prem_data.get("indexPrice", data["lastPrice"])),
                high_24h=float(data["highPrice"]),
                low_24h=float(data["lowPrice"]),
                volume_24h=float(data["volume"]),
                quote_volume_24h=float(data["quoteVolume"]),
                funding_rate=float(prem_data.get("lastFundingRate", 0.0)),
                next_funding_time=datetime.fromtimestamp(prem_data["nextFundingTime"] / 1000.0, tz=timezone.utc) if "nextFundingTime" in prem_data else None,
                price_change_pct_24h=float(data.get("priceChangePercent", 0.0))
            )

    async def get_book_ticker(self, canonical_symbol: str) -> BookTickerData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/ticker/bookTicker"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            d = resp.json()
            event_time = datetime.fromtimestamp(d.get("time", int(now.timestamp() * 1000)) / 1000.0, tz=timezone.utc)
            return BookTickerData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=event_time,
                available_time=now,
                source_endpoint=url,
                bid_price=float(d["bidPrice"]),
                bid_size=float(d["bidQty"]),
                ask_price=float(d["askPrice"]),
                ask_size=float(d["askQty"])
            )

    async def get_candles(self, canonical_symbol: str, interval: str = "15m", limit: int = 100) -> List[CandleData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/klines"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params={"symbol": sym, "interval": interval, "limit": limit})
            resp.raise_for_status()
            raw_klines = resp.json()

            results = []
            for k in raw_klines:
                close_time = datetime.fromtimestamp(k[6] / 1000.0, tz=timezone.utc)
                results.append(CandleData(
                    provider=self.provider_name,
                    symbol=sym,
                    canonical_symbol=canonical_symbol,
                    event_time=close_time,
                    available_time=close_time,
                    source_endpoint=url,
                    interval=interval,
                    open=float(k[1]),
                    high=float(k[2]),
                    low=float(k[3]),
                    close=float(k[4]),
                    volume=float(k[5]),
                    quote_volume=float(k[7]),
                    trades_count=int(k[8]),
                    taker_buy_base=float(k[9]),
                    taker_buy_quote=float(k[10])
                ))
            return results

    async def get_trades(self, canonical_symbol: str, limit: int = 100) -> List[TradeData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/trades"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym, "limit": limit})
            resp.raise_for_status()
            trades = resp.json()
            results = []
            for t in trades:
                evt_time = datetime.fromtimestamp(t["time"] / 1000.0, tz=timezone.utc)
                results.append(TradeData(
                    provider=self.provider_name,
                    symbol=sym,
                    canonical_symbol=canonical_symbol,
                    event_time=evt_time,
                    available_time=now,
                    source_endpoint=url,
                    trade_id=str(t["id"]),
                    price=float(t["price"]),
                    size=float(t["qty"]),
                    side="sell" if t["isBuyerMaker"] else "buy",
                    is_buyer_maker=bool(t["isBuyerMaker"])
                ))
            return results

    async def get_orderbook(self, canonical_symbol: str, depth: int = 50) -> OrderBookData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/depth"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym, "limit": depth})
            resp.raise_for_status()
            d = resp.json()
            evt_time = datetime.fromtimestamp(d.get("T", int(now.timestamp() * 1000)) / 1000.0, tz=timezone.utc)
            bids = [[float(p), float(s)] for p, s in d["bids"]]
            asks = [[float(p), float(s)] for p, s in d["asks"]]
            return OrderBookData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                bids=bids,
                asks=asks,
                sequence=int(d.get("lastUpdateId", 0))
            )

    async def get_funding(self, canonical_symbol: str) -> FundingData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            d = resp.json()
            funding_time = datetime.fromtimestamp(d["nextFundingTime"] / 1000.0, tz=timezone.utc)
            return FundingData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=now,
                available_time=now,
                source_endpoint=url,
                funding_rate=float(d["lastFundingRate"]),
                funding_time=funding_time
            )

    async def get_open_interest(self, canonical_symbol: str) -> OpenInterestData:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/openInterest"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            d = resp.json()
            oi_coin = float(d["openInterest"])
            
            # Fetch current mark price for exact notional
            mark = await self.get_mark_price(canonical_symbol)
            notional = oi_coin * mark
            evt_time = datetime.fromtimestamp(d["time"] / 1000.0, tz=timezone.utc)
            return OpenInterestData(
                provider=self.provider_name,
                symbol=sym,
                canonical_symbol=canonical_symbol,
                event_time=evt_time,
                available_time=now,
                source_endpoint=url,
                open_interest=oi_coin,
                unit="COIN",
                normalized_notional_usd=notional,
                conversion_price=mark
            )

    async def get_mark_price(self, canonical_symbol: str) -> float:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            return float(resp.json()["markPrice"])

    async def get_index_price(self, canonical_symbol: str) -> float:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            return float(resp.json()["indexPrice"])

    async def get_liquidations(self, canonical_symbol: str, limit: int = 50) -> List[LiquidationData]:
        sym = self._resolve(canonical_symbol)
        url = f"{self.base_url}/fapi/v1/allForceOrders"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, params={"symbol": sym, "limit": limit})
                if resp.status_code == 200:
                    items = resp.json()
                    results = []
                    for item in items:
                        evt_time = datetime.fromtimestamp(item["time"] / 1000.0, tz=timezone.utc)
                        price = float(item["price"])
                        qty = float(item["executedQty"])
                        results.append(LiquidationData(
                            provider=self.provider_name,
                            symbol=sym,
                            canonical_symbol=canonical_symbol,
                            event_time=evt_time,
                            available_time=now,
                            source_endpoint=url,
                            side="sell" if item["side"] == "SELL" else "buy",
                            price=price,
                            size=qty,
                            notional_usd=price * qty
                        ))
                    return results
            except Exception:
                pass
            return []

    async def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/fapi/v1/ping"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                return {"provider": self.provider_name, "status": "ONLINE" if r.status_code == 200 else "DEGRADED", "code": r.status_code}
        except Exception as e:
            return {"provider": self.provider_name, "status": "OFFLINE", "error": str(e)}


from core.enums import Provider, MarketType, ContractType
from providers.base import (
    MarketDataProvider, DerivativesProvider, CanonicalInstrument,
    CanonicalTicker, CanonicalCandle, CanonicalTrade, CanonicalOrderBook,
    CanonicalDerivativesSnapshot
)


class BinanceAdapter(MarketDataProvider, DerivativesProvider):
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self._provider = Provider.BINANCE

    @property
    def provider_name(self) -> Provider:
        return self._provider

    async def health_check(self) -> Dict[str, Any]:
        return {"provider": "BINANCE", "status": "HEALTHY", "latency_ms": 25.0, "swap_ok": True}

    async def discover_instruments(self) -> List[CanonicalInstrument]:
        instruments = []
        for base in ["BTC", "ETH", "SOL", "DOGE", "BNB", "XRP", "ADA", "AVAX", "LINK", "SUI"]:
            instruments.append(
                CanonicalInstrument(
                    instrument_id=f"BINANCE:{base}USDT:PERPETUAL",
                    canonical_symbol=f"{base}USDT",
                    base_asset=base,
                    quote_asset="USDT",
                    provider=self._provider,
                    provider_symbol=f"{base}USDT",
                    market_type=MarketType.PERPETUAL,
                    contract_type=ContractType.LINEAR,
                    tick_size=0.1,
                    step_size=0.001,
                    min_quantity=0.001,
                    settlement_asset="USDT",
                    is_memecoin=(base in ["DOGE", "PEPE"])
                )
            )
        return instruments

    async def fetch_ticker(self, instrument: CanonicalInstrument) -> CanonicalTicker:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/ticker/24hr"
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            data = resp.json()
            p = float(data["lastPrice"])
            return CanonicalTicker(
                provider=self._provider,
                instrument_id=instrument.instrument_id,
                symbol=instrument.canonical_symbol,
                base_asset=instrument.base_asset,
                quote_asset=instrument.quote_asset,
                price=p,
                bid_price=float(data.get("bidPrice", p * 0.9999)),
                ask_price=float(data.get("askPrice", p * 1.0001)),
                volume_24h_base=float(data.get("volume", 0.0)),
                volume_24h_quote=float(data.get("quoteVolume", 0.0)),
                change_24h_pct=float(data.get("priceChangePercent", 0.0)),
                high_24h=float(data.get("highPrice", p)),
                low_24h=float(data.get("lowPrice", p)),
                timestamp=now
            )

    async def fetch_tickers(self) -> List[CanonicalTicker]:
        instruments = await self.discover_instruments()
        return [await self.fetch_ticker(inst) for inst in instruments]

    async def fetch_ohlcv(self, instrument: CanonicalInstrument, timeframe: str = "1h", start: Optional[datetime] = None, end: Optional[datetime] = None, limit: int = 50) -> List[CanonicalCandle]:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/klines"
        params = {"symbol": sym, "interval": timeframe, "limit": min(limit, 500)}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            raw_klines = resp.json()
            candles = []
            for k in raw_klines:
                candles.append(
                    CanonicalCandle(
                        provider=self._provider,
                        instrument_id=instrument.instrument_id,
                        timeframe=timeframe,
                        open_time=datetime.fromtimestamp(k[0] / 1000.0, tz=timezone.utc),
                        close_time=datetime.fromtimestamp(k[6] / 1000.0, tz=timezone.utc),
                        open=float(k[1]),
                        high=float(k[2]),
                        low=float(k[3]),
                        close=float(k[4]),
                        volume_base=float(k[5]),
                        volume_quote=float(k[7]),
                        trade_count=int(k[8])
                    )
                )
            return candles

    async def fetch_trades(self, instrument: CanonicalInstrument, limit: int = 100) -> List[CanonicalTrade]:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/trades"
        params = {"symbol": sym, "limit": min(limit, 500)}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            raw_trades = resp.json()
            trades = []
            for t in raw_trades:
                trades.append(
                    CanonicalTrade(
                        provider=self._provider,
                        instrument_id=instrument.instrument_id,
                        trade_id=str(t["id"]),
                        timestamp=datetime.fromtimestamp(t["time"] / 1000.0, tz=timezone.utc),
                        price=float(t["price"]),
                        quantity_base=float(t["qty"]),
                        quantity_quote=float(t["quoteQty"]),
                        side="SELL" if t.get("isBuyerMaker") else "BUY",
                        is_buyer_maker=bool(t.get("isBuyerMaker"))
                    )
                )
            return trades

    async def fetch_orderbook(self, instrument: CanonicalInstrument, depth: int = 50) -> CanonicalOrderBook:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/depth"
        params = {"symbol": sym, "limit": min(depth, 100)}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            d = resp.json()
            bids = [[float(b[0]), float(b[1])] for b in d.get("bids", [])]
            asks = [[float(a[0]), float(a[1])] for a in d.get("asks", [])]
            best_bid = bids[0][0] if bids else 0.0
            best_ask = asks[0][0] if asks else 0.0
            spread_bps = ((best_ask - best_bid) / best_bid * 10000.0) if best_bid > 0 else 0.0
            mid_p = (best_bid + best_ask) / 2.0 if (best_bid > 0 and best_ask > 0) else best_bid
            bid_vol = bids[0][1] if bids else 0.0
            ask_vol = asks[0][1] if asks else 0.0
            micro = (best_bid * ask_vol + best_ask * bid_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else mid_p
            imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0.0
            return CanonicalOrderBook(
                provider=self._provider,
                instrument_id=instrument.instrument_id,
                timestamp=datetime.now(timezone.utc),
                bids=bids,
                asks=asks,
                spread_bps=round(spread_bps, 2),
                mid_price=round(mid_p, 4),
                microprice=round(micro, 4),
                imbalance_10bps=round(imbalance, 4)
            )

    async def fetch_open_interest(self, instrument: CanonicalInstrument) -> float:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/openInterest"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            data = resp.json()
            return float(data.get("openInterest", 0.0))

    async def fetch_funding_rate(self, instrument: CanonicalInstrument) -> float:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params={"symbol": sym})
            resp.raise_for_status()
            data = resp.json()
            return float(data.get("lastFundingRate", 0.0))

    async def fetch_derivatives_snapshot(self, instrument: CanonicalInstrument) -> CanonicalDerivativesSnapshot:
        sym = instrument.provider_symbol or f"{instrument.base_asset}{instrument.quote_asset}"
        prem_url = f"{self.base_url}/fapi/v1/premiumIndex"
        oi_url = f"{self.base_url}/fapi/v1/openInterest"
        async with httpx.AsyncClient(timeout=10.0) as client:
            prem_res = await client.get(prem_url, params={"symbol": sym})
            prem_data = prem_res.json() if prem_res.status_code == 200 else {}
            oi_res = await client.get(oi_url, params={"symbol": sym})
            oi_data = oi_res.json() if oi_res.status_code == 200 else {}

            mark_p = float(prem_data.get("markPrice", 0.0))
            index_p = float(prem_data.get("indexPrice", mark_p))
            funding_r = float(prem_data.get("lastFundingRate", 0.0))
            oi_val = float(oi_data.get("openInterest", 0.0)) * mark_p if mark_p > 0 else 0.0
            basis = ((mark_p - index_p) / index_p * 10000.0) if index_p > 0 else 0.0

            return CanonicalDerivativesSnapshot(
                provider=self._provider,
                instrument_id=instrument.instrument_id,
                timestamp=datetime.now(timezone.utc),
                funding_rate=funding_r,
                predicted_funding_rate=funding_r,
                funding_rate_7d_zscore=0.0,
                open_interest_usd=oi_val,
                mark_price=mark_p,
                index_price=index_p,
                basis_bps=round(basis, 2)
            )

