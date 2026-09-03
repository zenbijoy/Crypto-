"""
CryptoScope AI - Instrument Registry & Canonical Symbol Resolution
Maps exchange-specific symbols to internal canonical representations.
Example:
  Binance: BTCUSDT
  Bybit: BTCUSDT
  OKX: BTC-USDT-SWAP
  Canonical: BTC/USDT/PERP
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel


class InstrumentSpec(BaseModel):
    canonical_symbol: str
    provider: str
    provider_symbol: str
    base: str
    quote: str
    settlement: str
    contract_type: str = "PERP"
    tick_size: float
    step_size: float
    contract_multiplier: float = 1.0  # OKX contracts might be 0.01 BTC or 100 USD


class InstrumentRegistry:
    """Registry maintaining bidirectional mapping between venues and canonical instruments."""

    def __init__(self):
        self._canonical_to_provider: Dict[str, Dict[str, InstrumentSpec]] = {}
        self._provider_to_canonical: Dict[str, Dict[str, str]] = {}
        self._bootstrap_default_instruments()

    def _bootstrap_default_instruments(self):
        specs = [
            # BTC/USDT/PERP
            InstrumentSpec(
                canonical_symbol="BTC/USDT/PERP",
                provider="binance",
                provider_symbol="BTCUSDT",
                base="BTC",
                quote="USDT",
                settlement="USDT",
                tick_size=0.10,
                step_size=0.001,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="BTC/USDT/PERP",
                provider="bybit",
                provider_symbol="BTCUSDT",
                base="BTC",
                quote="USDT",
                settlement="USDT",
                tick_size=0.10,
                step_size=0.001,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="BTC/USDT/PERP",
                provider="okx",
                provider_symbol="BTC-USDT-SWAP",
                base="BTC",
                quote="USDT",
                settlement="USDT",
                tick_size=0.10,
                step_size=0.01,
                contract_multiplier=0.01  # 1 contract = 0.01 BTC on OKX
            ),
            # ETH/USDT/PERP
            InstrumentSpec(
                canonical_symbol="ETH/USDT/PERP",
                provider="binance",
                provider_symbol="ETHUSDT",
                base="ETH",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=0.001,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="ETH/USDT/PERP",
                provider="bybit",
                provider_symbol="ETHUSDT",
                base="ETH",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=0.01,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="ETH/USDT/PERP",
                provider="okx",
                provider_symbol="ETH-USDT-SWAP",
                base="ETH",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=0.1,
                contract_multiplier=0.1  # 1 contract = 0.1 ETH on OKX
            ),
            # SOL/USDT/PERP
            InstrumentSpec(
                canonical_symbol="SOL/USDT/PERP",
                provider="binance",
                provider_symbol="SOLUSDT",
                base="SOL",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=0.01,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="SOL/USDT/PERP",
                provider="bybit",
                provider_symbol="SOLUSDT",
                base="SOL",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=0.1,
                contract_multiplier=1.0
            ),
            InstrumentSpec(
                canonical_symbol="SOL/USDT/PERP",
                provider="okx",
                provider_symbol="SOL-USDT-SWAP",
                base="SOL",
                quote="USDT",
                settlement="USDT",
                tick_size=0.01,
                step_size=1.0,
                contract_multiplier=1.0  # 1 contract = 1 SOL on OKX
            )
        ]

        for s in specs:
            self.register(s)

    def register(self, spec: InstrumentSpec):
        if spec.canonical_symbol not in self._canonical_to_provider:
            self._canonical_to_provider[spec.canonical_symbol] = {}
        self._canonical_to_provider[spec.canonical_symbol][spec.provider] = spec

        if spec.provider not in self._provider_to_canonical:
            self._provider_to_canonical[spec.provider] = {}
        self._provider_to_canonical[spec.provider][spec.provider_symbol] = spec.canonical_symbol

    def resolve_provider_symbol(self, canonical_symbol: str, provider: str) -> Optional[str]:
        spec = self.get_spec(canonical_symbol, provider)
        return spec.provider_symbol if spec else None

    def resolve_canonical(self, provider_symbol: str, provider: str) -> Optional[str]:
        return self._provider_to_canonical.get(provider, {}).get(provider_symbol)

    def get_spec(self, canonical_symbol: str, provider: str) -> Optional[InstrumentSpec]:
        # Support short aliases e.g. "BTCUSDT" or "BTC" -> "BTC/USDT/PERP"
        if canonical_symbol in ["BTC", "BTCUSDT", "BTC/USDT"]:
            canonical_symbol = "BTC/USDT/PERP"
        elif canonical_symbol in ["ETH", "ETHUSDT", "ETH/USDT"]:
            canonical_symbol = "ETH/USDT/PERP"
        elif canonical_symbol in ["SOL", "SOLUSDT", "SOL/USDT"]:
            canonical_symbol = "SOL/USDT/PERP"
            
        return self._canonical_to_provider.get(canonical_symbol, {}).get(provider)


instrument_registry = InstrumentRegistry()
